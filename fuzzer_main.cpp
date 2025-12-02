#include <px4_platform_common/px4_config.h>
#include <px4_platform_common/module.h>
#define private public
#define protected public
#include <lib/motion_planning/PositionSmoothing.hpp>
#undef private
#undef protected

#include <mathlib/mathlib.h>
#include <matrix/math.hpp>
#include <iostream>
#include <vector>
#include <cstdlib> 
#include <cmath>
#include <chrono> 

using namespace matrix;

struct MapProjection {
    double ref_lat_rad;
    double ref_lon_rad;
    double ref_alt;
    bool initialized = false;

    void init(double lat, double lon, double alt) {
        ref_lat_rad = math::radians(lat);
        ref_lon_rad = math::radians(lon);
        ref_alt = alt;
        initialized = true;
    }

    Vector3f project(double lat, double lon, double alt) {
        if (!initialized) return Vector3f(0, 0, 0);
        double lat_rad = math::radians(lat);
        double lon_rad = math::radians(lon);
        const double earth_radius = 6371000.0;
        double x_north = (lat_rad - ref_lat_rad) * earth_radius;
        double y_east = (lon_rad - ref_lon_rad) * earth_radius * cos(ref_lat_rad);
        double z_down = -(alt - ref_alt); 
        return Vector3f((float)x_north, (float)y_east, (float)z_down);
    }
};

class FuzzablePositionSmoothing : public PositionSmoothing {
public:
    FuzzablePositionSmoothing() : PositionSmoothing() {}

    void injectConfig19(const std::vector<float>& p) {
        float acc_hor_usr = p[0];
        float acc_hor_hard_max = p[1];
        float tilt_max_deg = p[2];
        
        float tilt_rad = math::radians(math::constrain(tilt_max_deg, 0.0f, 85.0f));
        float acc_from_tilt = 9.81f * tanf(tilt_rad);
        float final_acc_xy = math::min(acc_hor_usr, acc_hor_hard_max);
        final_acc_xy = math::min(final_acc_xy, acc_from_tilt);

        float acc_down = p[3];
        float vel_xy_max = p[9];
        
        float vel_z_auto_up = p[11]; 
        float vel_z_auto_dn = p[13]; 
        
        float jerk_auto = p[6];
        float jerk_hard_max = p[5];
        float final_jerk = math::min(jerk_auto, jerk_hard_max);

        for (int i = 0; i < 2; ++i) { 
            _trajectory[i].setMaxAccel(final_acc_xy);
            _trajectory[i].setMaxVel(vel_xy_max);
            _trajectory[i].setMaxJerk(final_jerk);
        }

        _trajectory[2].setMaxAccel(acc_down);
        _trajectory[2].setMaxVel(math::max(vel_z_auto_up, vel_z_auto_dn)); 
        _trajectory[2].setMaxJerk(final_jerk);

        _cruise_speed = p[8]; 
        _target_acceptance_radius = 2.0f; 
        _max_allowed_horizontal_error = 5.0f; 
        _vertical_acceptance_radius = 0.8f;
        _horizontal_trajectory_gain = 0.5f;
    }
};

extern "C" __EXPORT int setpoint_fuzzer_main(int argc, char *argv[]);

void print_usage() {
    std::cout << "Usage: setpoint_fuzzer [P0]..[P18] [Lat1] [Lon1] [Alt1]..." << std::endl;
}

int setpoint_fuzzer_main(int argc, char *argv[]) {
    
    if (argc < 20) {
        print_usage();
        return 1;
    }

    std::vector<float> params;
    for (int i = 1; i <= 19; ++i) {
        params.push_back((float)atof(argv[i]));
    }

    std::vector<Vector3f> local_waypoints;
    MapProjection map_proj;
    
    int wp_start_idx = 20;
    int wp_args_count = argc - wp_start_idx;

    if (wp_args_count >= 3 && wp_args_count % 3 == 0) {
        for (int i = wp_start_idx; i < argc; i += 3) {
            double lat = atof(argv[i]);
            double lon = atof(argv[i+1]);
            double alt = atof(argv[i+2]);
            if (i == wp_start_idx) map_proj.init(lat, lon, alt);
            local_waypoints.push_back(map_proj.project(lat, lon, alt));
        }
    } else {
        map_proj.init(47.3977507, 8.5456074, 10.0);
        local_waypoints.push_back(map_proj.project(47.3977507, 8.5456074, 10.0));
        local_waypoints.push_back(map_proj.project(47.3979304, 8.5456074, 10.0));
        local_waypoints.push_back(map_proj.project(47.3979304, 8.5458728, 10.0));
        local_waypoints.push_back(map_proj.project(47.3977507, 8.5458728, 10.0));
        local_waypoints.push_back(map_proj.project(47.3977507, 8.5456074, 10.0));
        if (wp_args_count > 0) std::cerr << "Warning: Invalid waypoints. Using default." << std::endl;
    }

    FuzzablePositionSmoothing position_smoother;
    position_smoother.injectConfig19(params);

    Vector3f current_pos = local_waypoints[0];
    Vector3f current_vel(0,0,0);
    position_smoother.reset(Vector3f(0,0,0), current_vel, current_pos);

    float dt = 0.05f; 
    float time_now = 0.0f;
    int target_idx = 1; 
    int max_steps = 10000; 

    std::cout << "Time,PosX,PosY,PosZ,VelX,VelY,VelZ,AccX,AccY,AccZ,TargetIdx" << std::endl;

    auto start_time = std::chrono::high_resolution_clock::now();
    
    int steps_executed = 0; 

    for (int step = 0; step < max_steps; step++) {
        steps_executed++;

        Vector3f wp_prev = local_waypoints[target_idx - 1];
        Vector3f wp_curr = local_waypoints[target_idx];
        Vector3f wp_next = (target_idx + 1 < (int)local_waypoints.size()) ? local_waypoints[target_idx + 1] : wp_curr;

        Vector3f waypoints_triplet[3] = {wp_prev, wp_curr, wp_next};
        PositionSmoothing::PositionSmoothingSetpoints out;

        position_smoother._generateSetpoints(
            current_pos,
            waypoints_triplet,
            false, Vector3f(0,0,0), dt, false, out
        );

        std::cout << time_now << ","
                  << out.position(0) << "," << out.position(1) << "," << out.position(2) << ","
                  << out.velocity(0) << "," << out.velocity(1) << "," << out.velocity(2) << ","
                  << out.acceleration(0) << "," << out.acceleration(1) << "," << out.acceleration(2) << ","
                  << target_idx << std::endl;

        current_pos = out.position;
        
        float dist = (current_pos - wp_curr).length();
        if (dist < 2.0f) {
            if (target_idx < (int)local_waypoints.size() - 1) {
                target_idx++;
            } else {
                if (out.velocity.length() < 0.1f) break; 
            }
        }
        
        if (!PX4_ISFINITE(current_pos(0))) {
            std::cerr << "CRASH: NaN Generated" << std::endl;
            return 1; 
        }

        time_now += dt;
    }


    auto end_time = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end_time - start_time);
    
    std::cerr << "Total Execution Time: " << duration.count() << " us (" 
              << duration.count() / 1000.0 << " ms)" << std::endl;
    std::cerr << "Steps Executed: " << steps_executed << std::endl;
    std::cerr << "Avg Time per Step: " << (double)duration.count() / steps_executed << " us" << std::endl;

    return 0;
}

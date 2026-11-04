// Adapter only: trajectory mathematics are compiled from the supplied PX4 tree.
#include "auto_adapter.hpp"
#include <algorithm>
#include <array>
#include <cmath>
#include <vector>

#ifdef _WIN32
#define API extern "C" __declspec(dllexport)
#else
#define API extern "C" __attribute__((visibility("default")))
#endif

// time, target_index, position[3], velocity[3], acceleration[3], yaw, yawrate.
struct Result { std::vector<std::array<double, 13>> rows; int status = 1; };
enum Param { ACC, ACC_MAX, TILT, DOWN_ACC, UP_ACC, JERK_MAX, JERK,
             XY_ALL, CRUISE, XY_MAX, Z_ALL, UP, UP_MAX, DOWN, DOWN_MAX,
             TAKEOFF, LAND, LAND_TILT, YAW };

API int uav_abi_version() { return 2; }
API void *uav_run(const double *params, int param_count, const double *points,
                  int count, const int *types, const double *options, int option_count)
{
    if (!params || !points || !types || !options || option_count!=13 || param_count != 19 || count < 2) return nullptr;
    const double dt=options[0],duration=options[1],radius=options[2];
    if (dt<=0 || duration<=0 || radius<=0) return nullptr;
    auto *result = new Result;
    try {
        std::array<float,19> p;
        for (int i=0;i<19;++i) p[i]=static_cast<float>(params[i]);
        if (p[XY_ALL] >= 0) p[CRUISE]=p[XY_MAX]=p[XY_ALL];
        if (p[Z_ALL] >= 0) {
            p[UP]=p[UP_MAX]=p[Z_ALL];
            p[DOWN]=p[DOWN_MAX]=p[Z_ALL]*.75f;
            p[TAKEOFF]=p[Z_ALL]*.6f; p[LAND]=p[Z_ALL]*.5f;
        }
        if (p[CRUISE]>p[XY_MAX]) p[CRUISE]=p[XY_MAX];
        if (p[UP]>p[UP_MAX]) p[UP]=p[UP_MAX];
        if (p[DOWN]>p[DOWN_MAX]) p[DOWN]=p[DOWN_MAX];
        p[TAKEOFF]=math::min(p[TAKEOFF],p[UP_MAX]);
        p[LAND]=math::min(p[LAND],p[DOWN_MAX]);
        AutoAdapter task;
        task._param_mpc_acc_hor.value=p[ACC];
        task._param_mpc_acc_down_max.value=p[DOWN_ACC];
        task._param_mpc_acc_up_max.value=p[UP_ACC];
        task._param_mpc_xy_vel_max.value=p[XY_MAX];
        task._param_mpc_jerk_auto.value=p[JERK];
        task._mc_cruise_speed=p[CRUISE];
        task._param_mpc_z_v_auto_up.value=p[UP];
        task._param_mpc_z_v_auto_dn.value=p[DOWN];
        task._param_mpc_z_vel_max_up.value=p[UP_MAX];
        task._param_mpc_z_vel_max_dn.value=p[DOWN_MAX];
        task._param_mpc_tko_speed.value=p[TAKEOFF];
        task._param_mpc_xy_err_max.value=options[3];
        task._param_nav_mc_alt_rad.value=options[4];
        task._param_mpc_xy_traj_p.value=options[5];
        task._param_mpc_tko_ramp_t.value=options[6];
        const float land_alt2=options[8];
        task._param_mpc_land_alt1.value=math::max(static_cast<float>(options[7]),land_alt2);
        const float ground_z=options[9];
        task._param_mpc_yaw_mode.value=options[10];
        task._param_mis_yaw_err.value=options[11];
        task._param_mpc_yawrauto_max.value=p[YAW];
        task._yaw=task._yaw_setpoint=task._yaw_sp_prev=options[12];
        task._target_acceptance_radius=radius;
        task._deltatime=dt;
        auto &dut=task._position_smoothing;
        auto point = [&](int i) { return Vector3f(points[3*i],points[3*i+1],points[3*i+2]); };
        Vector3f state=point(0);
        task._sub_home_position.data.x=state(0);
        task._sub_home_position.data.y=state(1);
        dut.reset(Vector3f(),Vector3f(),state);
        int target=1;
        int previous_type=-1;
        float land_heading=task._yaw;
        const int max_steps=static_cast<int>(std::ceil(duration/dt));
        for (int step=0;step<max_steps && target<count;++step) {
            // Advance repeated or already accepted waypoints without taking a
            // spurious dynamics step. Index always denotes the scored segment.
            if ((state-point(target)).norm()<radius) { ++target; --step; continue; }
            task._position=state;
            task._target=point(target);
            task._type=static_cast<WaypointType>(types[target]);
            task._dist_to_ground=ground_z-state(2);
            task._set_heading_from_mode();
            Vector3f triplet[3]={point(target-1),point(target),point(std::min(target+1,count-1))};
            Vector3f feedforward(NAN,NAN,NAN);
            if (task._type==WaypointType::land) {
                // FlightTaskAuto::_prepareLandSetpoints(), non-RC branch.
                // Ideal ground height is supplied; no range sensor/crawl branch.
                if (previous_type!=types[target]) land_heading=task._yaw_setpoint;
                task._yaw_setpoint=land_heading;
                const float speed=math::interpolate(task._dist_to_ground,land_alt2,
                    task._param_mpc_land_alt1.get(),p[LAND],p[DOWN_MAX]);
                triplet[1](2)=NAN;
                triplet[2]=triplet[1];
                feedforward(2)=speed;
            }
            task._checkEmergencyBraking();
            const bool force_zero=(options[10]==4 && !task._yaw_sp_aligned) || task._is_emergency_braking_active;
            task._constraints.speed_up=p[UP_MAX];
            task._constraints.speed_down=p[DOWN_MAX];
            task._updateTrajConstraints();
            PositionSmoothing::PositionSmoothingSetpoints s;
            // PX4 may return without filling output for invalid velocity
            // targets. Poison the output so this cannot look like completion.
            s.position=s.velocity=s.acceleration=Vector3f(NAN,NAN,NAN);
            dut.generateSetpoints(state,triplet,feedforward,static_cast<float>(dt),force_zero,s);
            task._unsmoothed_velocity_setpoint=s.unsmoothed_velocity;
            task._velocity_setpoint=s.velocity;
            if (!PX4_ISFINITE(task._yaw_setpoint)) {
                if (!task._generateHeadingAlongTraj()) task._yaw_setpoint=task._yaw_sp_prev;
            }
            task._limitYawRate();
            std::array<double,13> row;
            row[0]=(step+1)*dt; row[1]=target;
            bool finite=true;
            for (int axis=0;axis<3;++axis) {
                row[2+axis]=s.position(axis); row[5+axis]=s.velocity(axis); row[8+axis]=s.acceleration(axis);
                finite=finite && std::isfinite(row[2+axis]) && std::isfinite(row[5+axis]) && std::isfinite(row[8+axis]);
            }
            row[11]=task._yaw_setpoint;
            row[12]=task._yawspeed_setpoint;
            finite=finite && std::isfinite(row[11]) && std::isfinite(row[12]);
            result->rows.push_back(row);
            if (!finite) { result->status=2; return result; }
            state=s.position; // Ideal state feedback, Algorithm 1 line 15.
            task._yaw=task._yaw_setpoint;
            previous_type=types[target];
            if ((state-point(target)).norm()<radius) ++target;
        }
        result->status=target==count?0:1;
        return result;
    } catch (...) { delete result; return nullptr; }
}
API int uav_status(const void *ptr) { return static_cast<const Result *>(ptr)->status; }
API int uav_count(const void *ptr) { return static_cast<int>(static_cast<const Result *>(ptr)->rows.size()); }
API const double *uav_data(const void *ptr) {
    const auto &r=static_cast<const Result *>(ptr)->rows; return r.empty()?nullptr:r.front().data();
}
API void uav_free(void *ptr) { delete static_cast<Result *>(ptr); }

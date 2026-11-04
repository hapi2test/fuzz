#pragma once
#include <motion_planning/PositionSmoothing.hpp>
#include <mathlib/mathlib.h>
#include <mathlib/math/filter/AlphaFilter.hpp>

// Narrow software harness for native FlightTaskAuto routines. No uORB,
// controller, RC nudging, estimator or vehicle dynamics are instantiated.
using namespace math;
using namespace matrix;
constexpr float CONSTANTS_ONE_G = 9.80665f;
struct ParamValue { float value; float get() const { return value; } };
enum class WaypointType { position=0, takeoff=1, land=2 };
enum class yaw_mode { towards_waypoint=0, towards_home=1, away_from_home=2,
                      along_trajectory=3, towards_waypoint_yaw_first=4, yaw_fixed=5 };
struct HomePosition { bool valid_lpos=true; float x=0,y=0; };
struct HomeSubscription { HomePosition data; const HomePosition &get() const { return data; } };

struct AutoAdapter {
    PositionSmoothing _position_smoothing;
    ParamValue _param_mpc_xy_err_max{2}, _param_nav_mc_alt_rad{.8f},
        _param_mpc_xy_traj_p{.5f}, _param_mpc_acc_hor{3}, _param_mpc_xy_vel_max{12},
        _param_mpc_jerk_auto{4}, _param_mpc_acc_up_max{4}, _param_mpc_acc_down_max{3},
        _param_mpc_z_v_auto_up{3}, _param_mpc_z_v_auto_dn{1.5f},
        _param_mpc_z_vel_max_up{3}, _param_mpc_z_vel_max_dn{1.5f},
        _param_mpc_tko_speed{1.5f}, _param_mpc_tko_ramp_t{3}, _param_mpc_land_alt1{10},
        _param_mpc_yawrauto_max{45}, _param_mis_yaw_err{12}, _param_mpc_yaw_mode{0};
    float _mc_cruise_speed=5, _target_acceptance_radius=.5f, _dist_to_ground=0,
          _deltatime=.02f, _yaw=0, _yaw_setpoint=0, _yaw_sp_prev=0,
          _yawspeed_setpoint=NAN;
    bool _is_emergency_braking_active=false, _yaw_sp_aligned=false, _yaw_lock=false;
    Vector3f _position, _target, _velocity_setpoint, _unsmoothed_velocity_setpoint;
    WaypointType _type=WaypointType::position;
    struct { float speed_up=3, speed_down=1.5f; } _constraints;
    HomeSubscription _sub_home_position;
    AlphaFilter<float> _yawspeed_filter;
    void _checkEmergencyBraking();
    void _updateTrajConstraints();
    void _limitYawRate();
    void _set_heading_from_mode();
    bool _generateHeadingAlongTraj();
    bool _compute_heading_from_2D_vector(float &heading, Vector2f v);
};

// Generated at build time from the supplied FlightTaskAuto.cpp. The only
// transformation is the enclosing class name; method bodies remain unchanged.
#include "auto_methods.generated.hpp"

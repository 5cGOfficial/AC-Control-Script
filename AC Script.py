AXIS_MAX = 32768
AXIS_HALF = int(AXIS_MAX * 0.5)
AXIS_QUARTER = int(AXIS_MAX * 0.25)

# Key states
w = keyboard.getKeyDown(Key.W)
s = keyboard.getKeyDown(Key.S)
ctrl = keyboard.getKeyDown(Key.LeftControl)
shift = keyboard.getKeyDown(Key.LeftShift)

# === Init ===
if starting:
    system.setThreadTiming(TimingTypes.HighresSystemTimer)
    system.threadExecutionInterval = 5

    import ctypes

    # Mouse and screen setup
    user32 = ctypes.windll.user32
    screen_width = user32.GetSystemMetrics(0)

    # vJoy axis limits (standard 15-bit range)
    vjoy_min = -16384
    vjoy_max = 16384

# === State Initialization ===
if 'throttle_current' not in globals():
    throttle_current = -16384
if 'brake_current' not in globals():
    brake_current = -16384
if 'throttle_target' not in globals():
    throttle_target = -16384
if 'brake_target' not in globals():
    brake_target = -16384

# === Target logic ===
if w and ctrl:
    throttle_target = -8192  # 25%
elif w and shift:
    throttle_target = 16384  # 100%
elif w:
    throttle_target = 0  # 50%
else:
    throttle_target = -16384  # No input

if s and ctrl:
    brake_target = -8192  # 25%
elif s and shift:
    brake_target = 16384  # 100%
elif s:
    brake_target = 0  # 50%
else:
    brake_target = -16384  # No input

# === Smooth Interpolation ===
speed = 1500

# Smooth throttle
if throttle_current < throttle_target:
    throttle_current = min(throttle_current + speed, throttle_target)
elif throttle_current > throttle_target:
    throttle_current = max(throttle_current - speed, throttle_target)

# Smooth brake
if brake_current < brake_target:
    brake_current = min(brake_current + speed, brake_target)
elif brake_current > brake_target:
    brake_current = max(brake_current - speed, brake_target)

# Apply to vJoy
vJoy[0].y = throttle_current
vJoy[0].z = brake_current

# === Mouse Steering Toggle ===
# === Mouse Steering Toggle (press + release toggles Piss) ===
if 'Piss' not in globals():
    Piss = True
if 'toggle_stage' not in globals():
    toggle_stage = 0

if toggle_stage == 0 and keyboard.getKeyDown(Key.LeftControl) and keyboard.getKeyDown(Key.M):
    toggle_stage = 1
elif toggle_stage == 1 and (not keyboard.getKeyDown(Key.LeftControl) or not keyboard.getKeyDown(Key.M)):
    Piss = not Piss
    toggle_stage = 0

# === Get mouse X position ===
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

if Piss == True:
    pt = POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    mouse_x = pt.x

    # Clamp and normalize
    mouse_x = max(0, min(mouse_x, screen_width))
    norm = float(mouse_x) / screen_width  # 0.0 to 1.0

    # Map to vJoy range
    vjoy_x = int(vjoy_min + (vjoy_max - vjoy_min) * norm)

    # Set vJoy steering axis
    vJoy[0].x = vjoy_x

    # Debug (optional)
    diagnostics.watch(vJoy[0].x)
    diagnostics.watch(mouse_x)

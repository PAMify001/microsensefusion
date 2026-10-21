import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)

# Simulate time steps (e.g., 200 readings over 10 seconds)
t = np.linspace(0, 10, 200)

# "Ground truth" — the real position of the robot tip, if we had a perfect sensor.
# A sine wave is just a simple stand-in for some smooth motion.
true_position = np.sin(t)

# Sensor A: noisy position reading (e.g., from an optical/vision sensor)
noise_A = np.random.normal(0, 0.3, size=t.shape)  # mean 0, fairly noisy
sensor_A = true_position + noise_A

# Sensor B: noisy position reading from a different sensing method
# (e.g., a force-derived estimate of position — different noise behavior)
noise_B = np.random.normal(0, 0.15, size=t.shape)  # less noisy than A
sensor_B = true_position + noise_B


# A complementary filter just takes a weighted average of the two sensors.
# Since sensor_B is less noisy here, we trust it more (give it a higher weight).
weight_B = 0.7
weight_A = 1 - weight_B

fused = (weight_A * sensor_A) + (weight_B * sensor_B)

# A very simple 1D Kalman filter
estimate = 0.0
error_estimate = 1.0
process_noise = 0.01
measurement_noise = 0.1

fused_kalman = []
for a, b in zip(sensor_A, sensor_B):
    measurement = (a + b) / 2  # combine both readings as one noisy measurement
    # Prediction step (assume estimate doesn't change much between steps)
    error_estimate += process_noise
    # Update step
    kalman_gain = error_estimate / (error_estimate + measurement_noise)
    estimate = estimate + kalman_gain * (measurement - estimate)
    error_estimate = (1 - kalman_gain) * error_estimate
    fused_kalman.append(estimate)

def rmse(est): return np.sqrt(np.mean((np.array(est) - true_position)**2))
for name, est in [("Sensor A", sensor_A), ("Sensor B", sensor_B),
                  ("Complementary", fused), ("Kalman", fused_kalman)]:
    print(name, round(rmse(est), 3))



# Figure 1: two sensors + complementary filter
plt.figure(figsize=(10, 5))
plt.plot(t, true_position, label="Ground Truth", linewidth=2, color="black")
plt.plot(t, sensor_A, label=f"Sensor A (RMSE {rmse(sensor_A):.3f})", alpha=0.5)
plt.plot(t, sensor_B, label=f"Sensor B (RMSE {rmse(sensor_B):.3f})", alpha=0.5)
plt.plot(t, fused, label=f"Complementary Fused (RMSE {rmse(fused):.3f})", linewidth=2, color="red")
plt.legend()
plt.title("Complementary filter fusion of two noisy sensors (synthetic data)")
plt.xlabel("Time (s)")
plt.ylabel("Position (arbitrary units)")
plt.savefig("fusion_complementary.png", dpi=200)
plt.show()

# Figure 2: Kalman
plt.figure(figsize=(10, 5))
plt.plot(t, true_position, label="Ground Truth", color="black", linewidth=2)
plt.plot(t, fused_kalman, label=f"Kalman Fused (RMSE {rmse(fused_kalman):.3f})", color="green")
plt.legend()
plt.title("Kalman filter fusion of two noisy sensors (synthetic data)")
plt.xlabel("Time (s)")
plt.ylabel("Position (arbitrary units)")
plt.savefig("fusion_kalman.png", dpi=200)
plt.show()
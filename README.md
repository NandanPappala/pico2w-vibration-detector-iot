# Machine Health Monitor

 

## IoT-Based Vibration Monitoring and Early Fault Detection System

 

### A Grade 12 passion project building an IoT vibration detector with a Pico 2 W and MPU6050 to monitor machine health.


 

---

 

# Project Overview

 

Machines naturally produce vibrations while operating. In some cases, unusual vibration patterns can indicate potential mechanical problems before they become serious.

 

This project uses an **MPU6050 sensor** connected to a **Raspberry Pi Pico 2W** to monitor vibration levels in real time. When vibration exceeds a predefined threshold, the system activates an LED and buzzer alert and sends the sensor data to an online dashboard using MQTT.

 

The project was developed to explore how sensors, embedded systems, wireless communication, and cloud platforms can work together to create a real-time monitoring solution.

 

---

 

# Features

 

- Real-time vibration monitoring

- Abnormal vibration detection

- LED warning indicator

- Buzzer alert notification

- MQTT-based wireless data transmission

- Adafruit IO dashboard integration

- Remote monitoring over Wi-Fi

 

---

 

# Motivation

 

I have always been interested in how technology can solve practical problems. While learning about sensors and IoT systems, I discovered that vibration monitoring is commonly used in industrial environments to identify potential equipment issues.

 

I decided to build a simplified version of a vibration monitoring system to better understand how hardware, software, and cloud services interact.

 

This project allowed me to gain experience in:

 

- Electronics

- Programming

- Internet of Things (IoT)

- Data Monitoring

- Troubleshooting

- Problem Solving

 

---

 

# Problem Statement

 

Many machines operate for long periods without constant supervision.

 

When abnormal vibrations occur:

 

- Problems may go unnoticed

- Equipment damage can worsen

- Repair costs can increase

- Unexpected downtime may occur

 

The goal of this project is to detect unusual vibration activity and notify users before a potential issue becomes more serious.

 

---

 

# System Architecture

 

```text

MPU6050 Sensor

│

▼

Measures Vibration

│

▼

Raspberry Pi Pico 2W

Processes Data

│

▼

Checks Threshold

│

┌────┴────┐

▼ ▼

LED Buzzer

Alert Alert

│

▼

MQTT over Wi-Fi

│

▼

Adafruit IO Dashboard

│

▼

Remote Monitoring

```

 

---

 

# Components Used

 

| Component | Purpose |

|------------|---------|

| Raspberry Pi Pico 2W | Main Controller |

| MPU6050 Sensor | Vibration Measurement |

| LED | Visual Alert |

| Buzzer | Audible Alert |

| Breadboard | Circuit Assembly |

| Jumper Wires | Electrical Connections |

| Wi-Fi | Wireless Communication |

| MQTT | Data Transmission |

| Adafruit IO | Cloud Dashboard |

 

---

 

# Wiring Connections

 

## MPU6050 Sensor

 

| MPU6050 Pin | Pico 2W Pin |

|-------------|-------------|

| VCC | 3.3V |

| GND | GND |

| SDA | GP0 |

| SCL | GP1 |

 

## LED

 

| Component | Pico Pin |

|-----------|----------|

| LED (+) | GP15 |

| LED (-) | GND |

 

## Buzzer

 

| Component | Pico Pin |

|-----------|----------|

| Buzzer (+) | GP16 |

| Buzzer (-) | GND |

 

---

 

# Hardware Setup

 

## Breadboard Assembly

 

Add a photo of your completed breadboard wiring.

 

```text

/images/breadboard-setup.jpg

```

 

## Circuit Diagram

 

Insert the circuit diagram here.

 

```text

/images/circuit-diagram.png

```

 

---

 

# Software and Tools

 

## Programming

 

- MicroPython

- Thonny IDE

 

## Communication

 

- Wi-Fi

- MQTT

 

## Cloud Platform

 

- Adafruit IO

 

---

 

# Getting Started

 

## Required Hardware

 

- Raspberry Pi Pico 2W

- MPU6050 Sensor

- LED

- Buzzer

- Breadboard

- Jumper Wires

 

## Setup

 

1. Assemble the circuit according to the wiring diagram.

2. Install MicroPython on the Raspberry Pi Pico 2W.

3. Configure Wi-Fi credentials.

4. Configure Adafruit IO credentials.

5. Upload the program using Thonny IDE.

6. Open the Adafruit IO dashboard.

7. Test the sensor by introducing vibration or movement.

 

---

 

# Dashboard Monitoring

 

The Raspberry Pi Pico publishes vibration data to Adafruit IO using MQTT.

 

The dashboard allows users to:

 

- Monitor vibration levels

- View alerts remotely

- Track sensor readings

- Access data online

 

## Dashboard Screenshot

 

Insert dashboard screenshot here.

 

```text

/images/dashboard.png

```

 

---

 

# Alert Logic

 

The system continuously measures vibration data and compares it against a predefined threshold.

 

When the threshold is exceeded:

 

- LED turns on

- Buzzer activates

- Data is sent to the dashboard

 

Example:

 

```python

if vibration > threshold:

led.on()

```

 

---

 

# Sample Results

 

| Vibration Level | System Status |

|----------------|--------------|

| 0.15g | Normal |

| 0.45g | Normal |

| 0.90g | Warning |

| 1.20g | Alert |

 

---

 

# Results

 

The completed system successfully:

 

- Measured vibration levels in real time

- Triggered visual alerts

- Triggered audible alerts

- Transmitted data wirelessly

- Updated a cloud dashboard

- Demonstrated a functional IoT monitoring solution

 

---

 

# Challenges

 

## Sensor Calibration

 

The MPU6050 occasionally produced noisy readings. Testing and adjusting threshold values helped improve consistency.

 

## Wi-Fi Connectivity

 

Establishing reliable wireless communication required troubleshooting network and MQTT settings.

 

## MQTT Communication

 

Learning how MQTT publishing and dashboard updates work was an important part of the project.

 

## Circuit Wiring

 

Several early issues were caused by incorrect wiring connections, reinforcing the importance of systematic testing and verification.

 

---

 

# What I Learned

 

This project helped me develop skills in:

 

- Internet of Things (IoT)

- Sensor Integration

- MicroPython Programming

- MQTT Messaging

- Circuit Design

- Cloud Dashboards

- Hardware Troubleshooting

- Real-Time Monitoring Systems

 

Most importantly, I learned how hardware and software can be combined to solve practical engineering problems.

 

---

 

# Future Improvements

 

Potential enhancements include:

 

- Email notifications

- SMS alerts

- Mobile application integration

- Multiple vibration sensors

- Historical data logging

- Machine learning-based fault detection

- Enhanced predictive maintenance capabilities

 

---

 

# Project Gallery

 

## Breadboard Setup

 

images/breadboard-setup.jpg

 

## Sensor Testing

 

images/sensor-testing.jpg

 

## Dashboard View

 

images/dashboard.png

 

## Alert Condition

 

images/alert-condition.jpg

 

---

 

# Demonstration Video

 

The demonstration includes:

 

1. Normal system operation

2. Sensor movement and vibration detection

3. Alert activation

4. Dashboard updates

 

## Video Link

 

[Insert YouTube or GitHub Video Link Here]

 

---

 

# Final Reflection

 

This project allowed me to combine electronics, programming, and IoT technologies to solve a practical problem. It provided valuable hands-on experience with sensors, wireless communication, and cloud-based monitoring systems.

 

The most rewarding part of the project was seeing the complete system function successfully from sensor measurement through to cloud dashboard visualization. It demonstrated how concepts learned in the classroom can be applied to real-world engineering challenges.

 

---

 

# Disclaimer

 

This project was developed as a Grade 12 Engineering and IoT passion project for educational purposes. The system demonstrates vibration monitoring using a Raspberry Pi Pico 2W and MPU6050 sensor and is intended for learning and experimentation only. It is not designed or certified for industrial safety, industrial monitoring, or production environments.

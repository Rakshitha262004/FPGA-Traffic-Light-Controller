# Project Report: FPGA-Based Traffic Light Controller

## Objective
Design and verify a synchronous FSM-based traffic light controller
for a two-way intersection, implementable on Xilinx FPGA hardware.

## FSM Design
4-state Moore FSM (S0–S3) controlling NS and EW light pairs.
See state table and encoding in README.

## RTL Explanation
- clock_divider.v: generates 1Hz tick from board clock
- traffic_light_controller.v: state register, next-state logic,
  output decode logic (3 always blocks: sequential, combinational
  next-state, combinational output)
- top_traffic_light.v: structural top-level wrapper

## Testbench Explanation
traffic_light_tb.v generates a 10ns-period clock, applies reset,
and runs the DUT with a reduced clock divisor for fast simulation.
Console monitor prints state on every active cycle; VCD dump
captures full waveform for inspection.

## Waveform Results
[Insert waveform_screenshot.png here]
Confirms correct cyclic transition S0→S1→S2→S3→S0 with correct
durations and mutually exclusive light outputs.

## FPGA Implementation
Synthesized and implemented in Vivado targeting [board part].
Utilization: [insert from report]
Timing: [insert from report, confirm no negative slack]

## Conclusion
Design correctly models a real traffic intersection controller
using standard synchronous digital design practices, verified
through simulation and FPGA synthesis flow.
// ============================================================
// Module: top_traffic_light
// Top-level wrapper: instantiates clock_divider + FSM controller.
// This is the module you synthesize for FPGA.
// ============================================================
module top_traffic_light #(
    parameter DIVISOR = 100_000_000   // 1Hz from a 100MHz board clock
)(
    input  wire clk,
    input  wire rst,

    output wire ns_red,
    output wire ns_yellow,
    output wire ns_green,
    output wire ew_red,
    output wire ew_yellow,
    output wire ew_green
);

    wire tick;

    clock_divider #(
        .DIVISOR(DIVISOR)
    ) u_clock_divider (
        .clk  (clk),
        .rst  (rst),
        .tick (tick)
    );

    traffic_light_controller u_fsm (
        .clk       (clk),
        .rst       (rst),
        .tick      (tick),
        .ns_red    (ns_red),
        .ns_yellow (ns_yellow),
        .ns_green  (ns_green),
        .ew_red    (ew_red),
        .ew_yellow (ew_yellow),
        .ew_green  (ew_green)
    );

endmodule
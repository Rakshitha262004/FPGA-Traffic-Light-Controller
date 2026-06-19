// ============================================================
// Module: clock_divider
// Converts a fast input clock into a slow 1Hz tick pulse.
// For simulation, DIVISOR is small so waveforms are readable.
// For real FPGA (100MHz), set DIVISOR = 100_000_000.
// ============================================================
module clock_divider #(
    parameter DIVISOR = 10   // small value for fast simulation
)(
    input  wire clk,
    input  wire rst,
    output reg  tick          // 1-cycle pulse every DIVISOR clk cycles
);

    reg [31:0] counter;

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            counter <= 32'd0;
            tick    <= 1'b0;
        end else begin
            if (counter == DIVISOR - 1) begin
                counter <= 32'd0;
                tick    <= 1'b1;
            end else begin
                counter <= counter + 1'b1;
                tick    <= 1'b0;
            end
        end
    end

endmodule
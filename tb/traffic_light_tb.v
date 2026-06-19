// ============================================================
// Testbench: traffic_light_tb
// Instantiates top_traffic_light with a SMALL divisor so the
// full FSM cycle completes quickly in simulation.
// ============================================================
`timescale 1ns/1ps

module traffic_light_tb;

    reg clk;
    reg rst;

    wire ns_red, ns_yellow, ns_green;
    wire ew_red, ew_yellow, ew_green;

    // Small divisor => fast simulation (tick every 10 clk cycles)
    top_traffic_light #(
        .DIVISOR(10)
    ) DUT (
        .clk       (clk),
        .rst       (rst),
        .ns_red    (ns_red),
        .ns_yellow (ns_yellow),
        .ns_green  (ns_green),
        .ew_red    (ew_red),
        .ew_yellow (ew_yellow),
        .ew_green  (ew_green)
    );

    // ---------------- Clock generation: 10ns period ----------------
    initial clk = 0;
    always #5 clk = ~clk;

    // ---------------- Reset + run ----------------
    initial begin
        rst = 1;
        #20;
        rst = 0;

        // Run long enough to see all 4 states cycle at least once.
        // Each state = (GREEN_TIME or YELLOW_TIME) * DIVISOR * 10ns
        // Total one full cycle ≈ (10+2+10+2)*10*10ns = 2400ns
        #6000;

        $display("Simulation complete.");
        $finish;
    end

    // ---------------- Waveform dump ----------------
    initial begin
        $dumpfile("traffic_light.vcd");
        $dumpvars(0, traffic_light_tb);
    end

    // ---------------- Monitor state changes on console ----------------
    always @(posedge clk) begin
        if (!rst) begin
            if (ns_green)
                $display("[%0t ns] STATE: NS-GREEN  | EW-RED", $time);
            else if (ns_yellow)
                $display("[%0t ns] STATE: NS-YELLOW | EW-RED", $time);
            else if (ew_green)
                $display("[%0t ns] STATE: NS-RED    | EW-GREEN", $time);
            else if (ew_yellow)
                $display("[%0t ns] STATE: NS-RED    | EW-YELLOW", $time);
        end
    end

endmodule
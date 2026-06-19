// ============================================================
// Module: traffic_light_controller
// 4-state Moore FSM controlling a 2-way (NS/EW) traffic light.
// Uses a 1Hz 'tick' input (from clock_divider) to count seconds.
// ============================================================
module traffic_light_controller (
    input  wire clk,
    input  wire rst,
    input  wire tick,          // 1Hz pulse

    output reg  ns_red,
    output reg  ns_yellow,
    output reg  ns_green,
    output reg  ew_red,
    output reg  ew_yellow,
    output reg  ew_green
);

    // State encoding
    localparam S0_NS_GREEN  = 2'b00;
    localparam S1_NS_YELLOW = 2'b01;
    localparam S2_EW_GREEN  = 2'b10;
    localparam S3_EW_YELLOW = 2'b11;

    // State durations (in seconds, i.e. number of ticks)
    localparam GREEN_TIME  = 10;
    localparam YELLOW_TIME = 2;

    reg [1:0]  current_state, next_state;
    reg [31:0] sec_counter;        // counts ticks within a state

    // ---------------- State register ----------------
    always @(posedge clk or posedge rst) begin
        if (rst)
            current_state <= S0_NS_GREEN;
        else if (tick)
            current_state <= next_state;
        else
            current_state <= current_state; // hold
    end

    // ---------------- Second counter -----------------
    always @(posedge clk or posedge rst) begin
        if (rst) begin
            sec_counter <= 32'd0;
        end else if (tick) begin
            if (current_state != next_state)
                sec_counter <= 32'd0;       // reset on state change
            else
                sec_counter <= sec_counter + 1'b1;
        end
    end

    // ---------------- Next-state logic ----------------
    always @(*) begin
        next_state = current_state; // default: stay
        case (current_state)
            S0_NS_GREEN:
                if (sec_counter >= GREEN_TIME - 1)
                    next_state = S1_NS_YELLOW;

            S1_NS_YELLOW:
                if (sec_counter >= YELLOW_TIME - 1)
                    next_state = S2_EW_GREEN;

            S2_EW_GREEN:
                if (sec_counter >= GREEN_TIME - 1)
                    next_state = S3_EW_YELLOW;

            S3_EW_YELLOW:
                if (sec_counter >= YELLOW_TIME - 1)
                    next_state = S0_NS_GREEN;

            default:
                next_state = S0_NS_GREEN;
        endcase
    end

    // ---------------- Output decode logic (Moore) ----------------
    always @(*) begin
        // default all off
        ns_red = 0; ns_yellow = 0; ns_green = 0;
        ew_red = 0; ew_yellow = 0; ew_green = 0;

        case (current_state)
            S0_NS_GREEN: begin
                ns_green = 1; ew_red = 1;
            end
            S1_NS_YELLOW: begin
                ns_yellow = 1; ew_red = 1;
            end
            S2_EW_GREEN: begin
                ns_red = 1; ew_green = 1;
            end
            S3_EW_YELLOW: begin
                ns_red = 1; ew_yellow = 1;
            end
        endcase
    end

endmodule
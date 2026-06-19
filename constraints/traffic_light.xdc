## Clock signal (100 MHz)
set_property PACKAGE_PIN W5 [get_ports clk]
set_property IOSTANDARD LVCMOS33 [get_ports clk]
create_clock -add -name sys_clk_pin -period 10.00 -waveform {0 5} [get_ports clk]

## Reset (push button)
set_property PACKAGE_PIN U18 [get_ports rst]
set_property IOSTANDARD LVCMOS33 [get_ports rst]

## NS LEDs
set_property PACKAGE_PIN U16 [get_ports ns_red]
set_property IOSTANDARD LVCMOS33 [get_ports ns_red]
set_property PACKAGE_PIN E19 [get_ports ns_yellow]
set_property IOSTANDARD LVCMOS33 [get_ports ns_yellow]
set_property PACKAGE_PIN U19 [get_ports ns_green]
set_property IOSTANDARD LVCMOS33 [get_ports ns_green]

## EW LEDs
set_property PACKAGE_PIN V19 [get_ports ew_red]
set_property IOSTANDARD LVCMOS33 [get_ports ew_red]
set_property PACKAGE_PIN W18 [get_ports ew_yellow]
set_property IOSTANDARD LVCMOS33 [get_ports ew_yellow]
set_property PACKAGE_PIN U15 [get_ports ew_green]
set_property IOSTANDARD LVCMOS33 [get_ports ew_green]
package pid_package
  model control_loop
    Modelica.Blocks.Math.Add add(k1 = -1)  annotation(
      Placement(visible = true, transformation(origin = {-54, 0}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Math.Add add1(k1 = -1)  annotation(
      Placement(visible = true, transformation(origin = {76, 0}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    pid_package.mech_car ego_car annotation(
      Placement(visible = true, transformation(origin = {30, 0}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    pid_package.lead_car forward_car annotation(
      Placement(visible = true, transformation(origin = {42, -30}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    parameter Real set_point = 10.0 "Desired Distance";
  
    Modelica.Blocks.Sources.Constant r_t(k = set_point) annotation(
      Placement(visible = true, transformation(origin = {-88, 0}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Interfaces.RealOutput e annotation(
      Placement(visible = true, transformation(origin = {-30, 0}, extent = {{-10, -10}, {10, 10}}, rotation = 0), iconTransformation(origin = {-30, 0}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Interfaces.RealInput u annotation(
      Placement(visible = true, transformation(origin = {8.88178e-16, -2.22045e-16}, extent = {{-12, -12}, {12, 12}}, rotation = 0), iconTransformation(origin = {6, 0}, extent = {{-20, -20}, {20, 20}}, rotation = 0)));
  equation
    connect(forward_car.y, add1.u2) annotation(
      Line(points = {{53, -30}, {65, -30}, {65, -6}, {64, -6}}, color = {0, 0, 127}));
    connect(r_t.y, add.u1) annotation(
      Line(points = {{-77, 0}, {-74, 0}, {-74, 6}, {-66, 6}}, color = {0, 0, 127}));
    connect(ego_car.y, add1.u1) annotation(
      Line(points = {{41, 0}, {59.5, 0}, {59.5, 6}, {64, 6}}, color = {0, 0, 127}));
  connect(add1.y, add.u2) annotation(
      Line(points = {{88, 0}, {90, 0}, {90, -80}, {-66, -80}, {-66, -6}}, color = {0, 0, 127}));
  connect(add.y, e) annotation(
      Line(points = {{-42, 0}, {-30, 0}}, color = {0, 0, 127}));
  connect(u, ego_car.u) annotation(
      Line(points = {{0, 0}, {18, 0}}, color = {0, 0, 127}));
    annotation(
      Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}})),
  __OpenModelica_simulationFlags(lv = "LOG_STATS", s = "dassl", variableFilter = ".*"));
  end control_loop;

  block lead_car
    output Modelica.Blocks.Interfaces.RealOutput y annotation(
      Placement(visible = true, transformation(origin = {0, 0}, extent = {{100, -10}, {120, 10}}, rotation = 0), iconTransformation(origin = {0, 0}, extent = {{100, -10}, {120, 10}}, rotation = 0)));
    Modelica.Blocks.Continuous.Integrator integrator annotation(
      Placement(visible = true, transformation(origin = {-16, -40}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Continuous.Integrator integrator1 annotation(
      Placement(visible = true, transformation(origin = {24, -40}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Tables.CombiTable1Ds combiTable1Ds(extrapolation = Modelica.Blocks.Types.Extrapolation.HoldLastPoint, smoothness = Modelica.Blocks.Types.Smoothness.ConstantSegments, table = [0, 1.75; 20, -0.75; 40, 0.5; 60, -3.25; 70, 0]) annotation(
      Placement(visible = true, transformation(origin = {-50, -40}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Sources.ContinuousClock continuousClock1 annotation(
      Placement(visible = true, transformation(origin = {-88, -40}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Math.Add3 add3 annotation(
      Placement(visible = true, transformation(origin = {70, 0}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Sources.Constant x_l0(k = 10) annotation(
      Placement(visible = true, transformation(origin = {-56, 0}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Sources.Constant v_l0(k = 2.5) annotation(
      Placement(visible = true, transformation(origin = {-56, 40}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Math.Product product annotation(
      Placement(visible = true, transformation(origin = {-16, 60}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  equation
    connect(integrator.y, integrator1.u) annotation(
      Line(points = {{-4, -40}, {12, -40}}, color = {0, 0, 127}));
    connect(combiTable1Ds.y[1], integrator.u) annotation(
      Line(points = {{-39, -40}, {-28, -40}}, color = {0, 0, 127}));
    connect(continuousClock1.y, combiTable1Ds.u) annotation(
      Line(points = {{-76, -40}, {-62, -40}}, color = {0, 0, 127}));
    connect(add3.y, y) annotation(
      Line(points = {{82, 0}, {110, 0}}, color = {0, 0, 127}));
    connect(integrator1.y, add3.u3) annotation(
      Line(points = {{36, -40}, {58, -40}, {58, -8}}, color = {0, 0, 127}));
    connect(x_l0.y, add3.u2) annotation(
      Line(points = {{-44, 0}, {58, 0}}, color = {0, 0, 127}));
    connect(continuousClock1.y, product.u1) annotation(
      Line(points = {{-76, -40}, {-72, -40}, {-72, 66}, {-28, 66}}, color = {0, 0, 127}));
    connect(v_l0.y, product.u2) annotation(
      Line(points = {{-44, 40}, {-28, 40}, {-28, 54}}, color = {0, 0, 127}));
    connect(product.y, add3.u1) annotation(
      Line(points = {{-4, 60}, {58, 60}, {58, 8}}, color = {0, 0, 127}));
    annotation(
      Icon(graphics = {Rectangle(extent = {{-100, 100}, {100, -100}}), Text(textColor = {0, 0, 255}, extent = {{-150, 150}, {150, 110}}, textString = "%name")}, coordinateSystem(extent = {{-100, -100}, {100, 100}})));
  end lead_car;

  block PID_controller
    parameter Real k_p = 100.0 "Gain value position";
    parameter Real k_i = 1.0 "Gain value integrator";
    parameter Real k_d = 20.0 "Gain value derivative";
    
    output Modelica.Blocks.Interfaces.RealOutput u_t annotation(
      Placement(visible = true, transformation(origin = {-40, 0}, extent = {{100, -10}, {120, 10}}, rotation = 0), iconTransformation(origin = {0, 0}, extent = {{100, -10}, {120, 10}}, rotation = 0)));
    input Modelica.Blocks.Interfaces.RealInput e_t annotation(
      Placement(visible = true, transformation(origin = {-80, 0}, extent = {{-20, -20}, {20, 20}}, rotation = 0), iconTransformation(origin = {-120, 0}, extent = {{-20, -20}, {20, 20}}, rotation = 0)));
    Modelica.Blocks.Continuous.Integrator integrator(k = k_i)  annotation(
      Placement(visible = true, transformation(origin = {-20, 0}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Math.Gain gain(k = k_p) annotation(
      Placement(visible = true, transformation(origin = {-20, 40}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Continuous.Derivative derivative(k = k_d) annotation(
      Placement(visible = true, transformation(origin = {-20, -40}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Math.Add3 add3 annotation(
      Placement(visible = true, transformation(origin = {24, 0}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  equation
    connect(e_t, integrator.u) annotation(
      Line(points = {{-80, 0}, {-32, 0}}, color = {0, 0, 127}));
    connect(e_t, derivative.u) annotation(
      Line(points = {{-80, 0}, {-50, 0}, {-50, -40}, {-32, -40}}, color = {0, 0, 127}));
    connect(e_t, gain.u) annotation(
      Line(points = {{-80, 0}, {-50, 0}, {-50, 40}, {-32, 40}}, color = {0, 0, 127}));
    connect(gain.y, add3.u1) annotation(
      Line(points = {{-9, 40}, {-1, 40}, {-1, 8}, {11, 8}}, color = {0, 0, 127}));
    connect(derivative.y, add3.u3) annotation(
      Line(points = {{-9, -40}, {-1, -40}, {-1, -8}, {11, -8}}, color = {0, 0, 127}));
    connect(integrator.y, add3.u2) annotation(
      Line(points = {{-9, 0}, {11, 0}}, color = {0, 0, 127}));
    connect(add3.y, u_t) annotation(
      Line(points = {{35, 0}, {70, 0}}, color = {0, 0, 127}));
    annotation(
      Icon(graphics = {Rectangle(extent = {{-100, 100}, {100, -100}}), Text(textColor = {0, 0, 255}, extent = {{-150, 150}, {150, 110}}, textString = "%name")}, coordinateSystem(extent = {{-100, -100}, {100, 100}})),
  __OpenModelica_simulationFlags(lv = "LOG_STATS", noRestart = "()", s = "dassl", variableFilter = ".*"));
  end PID_controller;

  block mech_car
    import Modelica.Blocks.Types.Init;
    extends Modelica.Blocks.Interfaces.SISO;
    // Components
    final Modelica.Mechanics.Translational.Components.Vehicle vehicle(m = 8000, J = 0.01, R(displayUnit = "mm") = 0.24765, s(start = 0), v(start = 0), A = 2, Cd = 0.31) annotation(
      Placement(transformation(origin = {16, 0}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Mechanics.Translational.Sensors.PositionSensor positionSensor annotation(
      Placement(transformation(origin = {48, 0}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Mechanics.Rotational.Sources.Torque torque annotation(
      Placement(transformation(origin = {-14, 0}, extent = {{-10, -10}, {10, 10}})));
    final Modelica.Blocks.Math.Gain gain(k = 60) annotation(
      Placement(transformation(origin = {-48, 0}, extent = {{-10, -10}, {10, 10}})));
    // Connections
    Modelica.Mechanics.Translational.Sensors.SpeedSensor speedSensor annotation(
      Placement(transformation(origin = {48, -24}, extent = {{-10, -10}, {10, 10}})));
    Modelica.Mechanics.Translational.Sensors.AccSensor accSensor annotation(
      Placement(transformation(origin = {48, -44}, extent = {{-10, -10}, {10, 10}})));
  equation
    connect(vehicle.flangeT, positionSensor.flange) annotation(
      Line(points = {{26, 0}, {38, 0}}, color = {0, 127, 0}));
    connect(positionSensor.s, y) annotation(
      Line(points = {{59, 0}, {110, 0}}, color = {0, 0, 127}));
    connect(torque.flange, vehicle.flangeR) annotation(
      Line(points = {{-4, 0}, {6, 0}}));
    connect(gain.y, torque.tau) annotation(
      Line(points = {{-37, 0}, {-27, 0}}, color = {0, 0, 127}));
    connect(gain.u, u) annotation(
      Line(points = {{-60, 0}, {-120, 0}}, color = {0, 0, 127}));
    connect(speedSensor.flange, vehicle.flangeT) annotation(
      Line(points = {{38, -24}, {32, -24}, {32, 0}, {26, 0}}, color = {0, 127, 0}));
    connect(accSensor.flange, vehicle.flangeT) annotation(
      Line(points = {{38, -44}, {32, -44}, {32, 0}, {26, 0}}, color = {0, 127, 0}));
  end mech_car;
  annotation(
    uses(Modelica(version = "4.0.0")));
end pid_package;

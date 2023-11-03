package pid_package
  model control_loop
    Modelica.Blocks.Math.Add add annotation(
      Placement(visible = true, transformation(origin = {-54, 0}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    pid_package.PID_controller pID_controller annotation(
      Placement(visible = true, transformation(origin = {-22, 0}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Math.Gain negate(k = -1) annotation(
      Placement(visible = true, transformation(origin = {-10, -80}, extent = {{10, -10}, {-10, 10}}, rotation = 0)));
    Modelica.Blocks.Math.Gain negate1(k = -1) annotation(
      Placement(visible = true, transformation(origin = {42, 0}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Math.Add add1 annotation(
      Placement(visible = true, transformation(origin = {76, 0}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    pid_package.mech_car mech_car annotation(
      Placement(visible = true, transformation(origin = {10, 0}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    pid_package.lead_car lead_car annotation(
      Placement(visible = true, transformation(origin = {30, -30}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Sources.Constant r_t(k = 10) annotation(
      Placement(visible = true, transformation(origin = {-88, 0}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  equation
    connect(add.y, pID_controller.e_t) annotation(
      Line(points = {{-42, 0}, {-34, 0}}, color = {0, 0, 127}));
    connect(negate.y, add.u2) annotation(
      Line(points = {{-20, -80}, {-66, -80}, {-66, -6}}, color = {0, 0, 127}));
    connect(negate1.y, add1.u1) annotation(
      Line(points = {{54, 0}, {56, 0}, {56, 6}, {64, 6}}, color = {0, 0, 127}));
    connect(add1.y, negate.u) annotation(
      Line(points = {{88, 0}, {92, 0}, {92, -80}, {2, -80}}, color = {0, 0, 127}));
    connect(pID_controller.u_t, mech_car.u) annotation(
      Line(points = {{-11, 0}, {-2, 0}}, color = {0, 0, 127}));
    connect(mech_car.y, negate1.u) annotation(
      Line(points = {{21, 0}, {30, 0}}, color = {0, 0, 127}));
    connect(lead_car.x_lt, add1.u2) annotation(
      Line(points = {{42, -30}, {64, -30}, {64, -6}}, color = {0, 0, 127}));
    connect(r_t.y, add.u1) annotation(
      Line(points = {{-77, 0}, {-74, 0}, {-74, 6}, {-66, 6}}, color = {0, 0, 127}));
    annotation(
      Diagram(coordinateSystem(extent = {{-100, -100}, {100, 100}})));
  end control_loop;

  block lead_car
    output Modelica.Blocks.Interfaces.RealOutput x_lt annotation(
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
    connect(add3.y, x_lt) annotation(
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
    parameter Real k_p = 1.0 "Gain value position";
    parameter Real k_i = 1.0 "Gain value integrator";
    parameter Real k_d = 20.0 "Gain value derivative";
    
    output Modelica.Blocks.Interfaces.RealOutput u_t annotation(
      Placement(visible = true, transformation(origin = {0, 0}, extent = {{100, -10}, {120, 10}}, rotation = 0), iconTransformation(origin = {0, 0}, extent = {{100, -10}, {120, 10}}, rotation = 0)));
    input Modelica.Blocks.Interfaces.RealInput e_t annotation(
      Placement(visible = true, transformation(origin = {-120, 0}, extent = {{-20, -20}, {20, 20}}, rotation = 0), iconTransformation(origin = {-120, 0}, extent = {{-20, -20}, {20, 20}}, rotation = 0)));
    Modelica.Blocks.Continuous.Integrator integrator(k = k_i)  annotation(
      Placement(visible = true, transformation(origin = {-50, 0}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Math.Gain gain(k = k_p) annotation(
      Placement(visible = true, transformation(origin = {-50, 40}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Continuous.Derivative derivative(k = k_d) annotation(
      Placement(visible = true, transformation(origin = {-50, -40}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
    Modelica.Blocks.Math.Add3 add3 annotation(
      Placement(visible = true, transformation(origin = {-6, 0}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  equation
    connect(e_t, integrator.u) annotation(
      Line(points = {{-120, 0}, {-62, 0}}, color = {0, 0, 127}));
    connect(e_t, derivative.u) annotation(
      Line(points = {{-120, 0}, {-80, 0}, {-80, -40}, {-62, -40}}, color = {0, 0, 127}));
    connect(e_t, gain.u) annotation(
      Line(points = {{-120, 0}, {-80, 0}, {-80, 40}, {-62, 40}}, color = {0, 0, 127}));
    connect(gain.y, add3.u1) annotation(
      Line(points = {{-38, 40}, {-30, 40}, {-30, 8}, {-18, 8}}, color = {0, 0, 127}));
    connect(derivative.y, add3.u3) annotation(
      Line(points = {{-38, -40}, {-30, -40}, {-30, -8}, {-18, -8}}, color = {0, 0, 127}));
    connect(integrator.y, add3.u2) annotation(
      Line(points = {{-38, 0}, {-18, 0}}, color = {0, 0, 127}));
    connect(add3.y, u_t) annotation(
      Line(points = {{6, 0}, {110, 0}}, color = {0, 0, 127}));
    annotation(
      Icon(graphics = {Rectangle(extent = {{-100, 100}, {100, -100}}), Text(textColor = {0, 0, 255}, extent = {{-150, 150}, {150, 110}}, textString = "%name")}, coordinateSystem(extent = {{-100, -100}, {100, 100}})));
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

import Beamprop_API as Beam

Beamprop_class = Beam.BeamProp("Test.ind")
Beamprop_class.change_variable("wg_Angle", 2)
print(Beamprop_class.read_variable("wg_Angle"))
Beamprop_class.change_simulation("mode", mode_method=0)
Beamprop_class.launch_simulation("Test_output")

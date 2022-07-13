import os


class BeamProp:
    def __init__(self, file_beam_prop):
        """
        To initialize the class you need just to insert the Beamprop file name
        """
        self.file = file_beam_prop
        f = open(self.file, "r")
        lines = f.readlines()

        self.DictionaryTaper = \
            {
                "type": "UF_DATAFILE",
                "filename": "$TaperName"
            }
        self.create_block("user_taper 1", "end user_taper", self.DictionaryTaper)

        self.DictionaryMonitor = \
            {
                "pathway": "0",
                "monitor_type": "Monitor",
                "monitor_tilt": "1",
                "monitor_component": "COMPONENT_BOTH",
                "monitor_file": "$ModeName",
            }
        self.create_block("monitor 1", "end monitor", self.DictionaryMonitor)

        self.DictionaryLaunch =\
            {
                "launch_pathway": "0",
                "launch_type": "LAUNCH_WGMODE",
                "launch_position": "0",
                "launch_position_y": "0"
            }
        self.create_block("launch_field 1", "end launch_field", self.DictionaryLaunch)

        # CHECK PATHWAY
        pathway = False
        for line in lines:
            if "end pathway" in line:
                pathway = True
                break
        if not pathway:
            print("\nPay attention, no pathway was detected. Create one to use monitor!\n")

        # CHECK START END SYMBOL PRESENCE
        if "#symbols_start" not in lines[0]:
            lines.insert(0, "#symbols_start")
            print("Symbol start added")

        for idx, line in enumerate(lines[:-1]):
            if "#symbols_end" in line:
                break
            if len(lines[idx]) == 1 and len(lines[idx + 1]) == 1:
                lines.insert(idx, "#symbols_end")
                print("Symbol end added")
                break

        f.close()

        f = open(self.file, "w")
        f.writelines(lines)
        f.close()

        # ADD USEFUL VARIABLES TO MONITOR AND TO CREATE TAPERS
        self.change_variable('Monitor', 'MONITOR_FILE_POWER')
        self.change_variable('ModeName', '0')
        self.change_variable('TaperName', '0')

        return

    def create_block(self, block_name_start, block_name_end, block_dictionary):
        """
        This function creates a block that can be used inside Beamprop such as a Taper, a Monitor or a Launch field.
        block_name_start should contain the name of the block with the correspondent number: ex user_taper 1.
        block_name_end should contain the end of the block without the number: ex end user_taper.
        block_dictionary should contain all the elements of the block.
        """

        f = open(self.file, "r")
        lines = f.readlines()

        symbol_idx = 0
        symbol_idx_end = 0
        already_created = False
        for idx, line in enumerate(lines):
            if block_name_start in line:
                symbol_idx = idx + 1
                print("The block " + block_name_start + " was already present!")
                already_created = True
            if block_name_end in line:
                symbol_idx_end = idx + 1
                break
            if '#symbols_end' in line:
                symbol_idx = idx + 1

        block = "\n" + block_name_start + "\n"
        for key, val in block_dictionary.items():
            block += "	" + key + " = " + val + "\n"
        block += block_name_end

        if already_created:
            for i in reversed(range(symbol_idx - 1, symbol_idx_end)):
                lines.remove(lines[i])
            symbol_idx -= 2
            lines[symbol_idx] = block + lines[symbol_idx]
        else:
            lines[symbol_idx] = block + "\n" + lines[symbol_idx]

        f.close()

        f = open(self.file, "w")
        f.writelines(lines)
        f.close()
        return

    def change_variable(self, variable_name, variable_value):
        """
        This function assign the variable_value to the variable_name in the file_name.
        If the variable does not exist, the function will create it.
        """
        f = open(self.file, "r")
        lines = f.readlines()
        for idx, line in enumerate(lines):
            line_cur = line.split()
            if '#symbols_end' in line:
                print("Variable " + variable_name + " not found. The variable will now be added.")
                lines[idx] = variable_name + " = " + str(variable_value) + "\n#symbols_end\n"
                break
            if variable_name == line_cur[0]:
                lines[idx] = variable_name + " = " + str(variable_value) + "\n"
                break
        f.close()

        f = open(self.file, "w")
        f.writelines(lines)
        f.close()
        return

    def read_variable(self, variable_name):
        """
        This function print the variable_value from the variable_name in the file_name.
        """
        f = open(self.file, "r")
        lines = f.readlines()

        for idx, line in enumerate(lines):
            line_cur = line.split()
            if '#symbols_end' in line:
                print("Variable " + variable_name + " not found. Impossible read its value.")
                return False
            if variable_name == line_cur[0]:
                f.close()
                return float(line_cur[2])

    def eliminate_variable(self, variable_name):
        """
           This function eliminate the variable_name from the file_name.
        """

        f = open(self.file, "r")
        lines = f.readlines()
        for idx, line in enumerate(lines):
            line_cur = line.split()
            if '#symbols_end' in line:
                print("Variable " + variable_name + " was already absent.")
                break
            if variable_name == line_cur[0]:
                lines.remove(lines[idx])
                break
        f.close()

        f = open(self.file, "w")
        f.writelines(lines)
        f.close()
        return

    def launch_simulation(self, output_name, hide=False, output_folder=None):
        """ This function launches the Beamprop file_name and create an output_name file with the results.
            It moves the output_name file in the output_folder if one is provided.
            Remember to change the simulation kind before launching this function.
            Leave the output_folder void to not move the files.
            The hide variable is used to launch the simulation without any window on screen."""

        if hide:
            os.system("bsimw32 -hide " + self.file + " prefix=" + output_name + " wait=0 idbpm_convergence_warning=0")
        else:
            os.system("bsimw32 " + self.file + " prefix=" + output_name + " wait=0 idbpm_convergence_warning=0")

        if output_folder is not None:
            if not os.path.isdir(output_folder):
                os.mkdir(output_folder)
            os.system("move " + output_name + "* " + output_folder)
        return

    def change_simulation(self, simulation_type, mode_n=None, mode_method=None):
        """
        This function change the kind of simulation you want to launch.
        Simulation_type could be propagation or mode.
        If simulation_type is mode, also mode_n and mode_method must be set.
        mode_n = the range of modes to find. mode_n = 0; mode_n = (1, 2)
        mode_method = 0 is the correlation method. mode_method = 1 is the iterative method
        """

        if simulation_type == 'mode':
            self.change_variable("mode_set", mode_n)
            self.change_variable('mode_method', mode_method)

        elif simulation_type == 'propagation':
            self.eliminate_variable("mode_set")
            self.eliminate_variable("mode_method")

        return

    def change_output_display(self, section):
        """
        This function is a case of change variable adapt to change the kind of display of the output.
        """

        if section == "xz" or section == "XZ" or section == "zx" or section == "ZX":
            self.change_variable("slice_display_mode", "DISPLAY_CONTOURMAPXZ")
        elif section == "yz" or section == "YZ" or section == "zy" or section == "ZY":
            self.change_variable("slice_display_mode", "DISPLAY_CONTOURMAPYZ")
        elif section == "xy" or section == "XY" or section == "yx" or section == "YX":
            self.change_variable("slice_display_mode", "DISPLAY_CONTOURMAPXY")
        else:
            print("Please, select a valid section name!")
        return

    @staticmethod
    def create_taper_file(self, output_name, data, output_folder=None):
        """
        This function creates a file output_name containing the data for a taper that can be used by a beamprop file.
        """
        f = open(output_name, "w")
        content = "/rn,a,b/nx0\n" + str(len(data)) + " 0 1 0 OUTPUT_REAL\n"
        for i in range(len(data)):
            content += str(data[i]) + "\n"
        f.write(content)
        f.close()

        if output_folder is not None:
            if not os.path.isdir(output_folder):
                os.mkdir(output_folder)
            os.system("move " + output_name + "* " + output_folder)
        return

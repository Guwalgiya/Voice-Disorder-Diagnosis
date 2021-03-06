# ===============================================
# Import Packages and Functions
from   os         import walk
import numpy      as     np
import subprocess
import math


# ===============================================
# Environment
pitch_shift_tool = "C:\\Archived Projects\\Voice-Disorder-Diagnosis\\_Others\\Pitchshifter\\elastiqueProCl.exe"
parent_path      = "C:\\Archived Projects\\Voice-Disorder-Diagnosis\\_Others\\Dataset-"
slash            = "\\"


# ===============================================
# Dataset Initialization
classes      = ["Normal", "Pathol"]
dataset_name = "Spanish"
dataset_path = parent_path + dataset_name


# ===============================================
# DSP Initialization
fs            = 25000
num_semitones = 4


# ===============================================
def pitch_shifting(a_class, pitch_shift_tool, num_semitones):


    # ===============================================
    input_main_folder  = dataset_path + slash + a_class;
    output_main_folder = dataset_path + slash + a_class + "_Pitch_Shifted"


    # ===============================================
    file_list = []
    for (dirpath, dirnames, filenames) in walk(input_main_folder):
        file_list.extend(filenames)
        break
    

    # ===============================================
    for filename in file_list:
        input_path = input_main_folder + slash + filename
        

        # ===============================================
        for step in np.linspace(0, num_semitones, num_semitones / 0.5 + 1):


            # ===============================================
            if step == 0: 
                output_path = output_main_folder + slash + filename[0: len(filename) - 4] + "_" + "N" + str(step) + ".wav"
                

                # ===============================================
                subprocess.Popen([pitch_shift_tool, "-i", input_path, "-o", output_path, "-s", "1", "-p", "1"]).wait()
                print(filename, step, 'done')
                

            # ===============================================    
            else:
                output_path = output_main_folder + slash + filename[0: len(filename) - 4] + "_" + "U" + str(step) + ".wav"
                ratio       = math.pow(2, step * 100 / 1200)


                # ===============================================
                subprocess.Popen([pitch_shift_tool, "-i", input_path, "-o", output_path, "-s", "1", "-p", str(ratio)]).wait()
                print(filename, step, 'done')
                

                # ===============================================
                output_path = output_main_folder + slash + filename[0: len(filename) - 4] + "_" + "D" + str(step) + ".wav"
                ratio       = math.pow(2, -1 * step * 100 / 1200)


                # ===============================================
                subprocess.Popen([pitch_shift_tool, "-i", input_path, "-o", output_path, "-s", "1", "-p", str(ratio)]).wait()
                print(filename, -1 * step, 'done')


# ===============================================
# Run this script, this script should be run before augmentation_block_audio
for a_class in classes:
    pitch_shifting(a_class, pitch_shift_tool, num_semitones)       
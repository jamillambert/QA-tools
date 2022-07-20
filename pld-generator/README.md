//============================================================================
// Name        : multipleLayerPBS.cpp
// Author      : D. Schoenenberg, J. Lambert 2011
// Version     : 2.0
// Copyright   :
// Description : writes a *.pld file for a multiple layer PBS beam
//               the spot weights within a layer are homogeneous
//               but there are different weights per layer.
//============================================================================

* The program can be run without any arguments and the variables entered at runtime.

OR

usage for a single layer:

multipleLayerPBS.exe <Range (g/cm�)> <FieldSizeX (mm)> <FieldSizeY (mm)> <SpotSpacing (mm)>  <total MU>

Note CB: <total MU> is really the number of MU of all spots.

OR

multipleLayerPBS -n < input

-n suppresses the output of the menu for every command in the input file.

"input" is an input file with the following commands seperated by a space or newline:

"setDefaults" - sets the values to default

"setVariables" - sets the variables manually, must be followed by a list of 8 numbers for the settings in this order:
		<range> <field size in x> <field size in y> <SOBP width> <spot spacing> <layer spacing> <number of MUs> <number of paintings>

"readWeights" <weight file name> - reads in layer weights from the specified file, weights file is a list of numbers with a . decimal seperator, the weights are for the highest energy layer to the lowest, the file must have at least as many weights as the number of layers with no other characters in the file except the weight numbers, but it can have more weights than the number used.

"writeFile" - writes the specified field to a pld file which is automatically named as "PBSfield_<max energy>_<x size>x<y size>x<SOBP width>_<number of MUs>.pld and overwrites any existing pld file with the same name.

"exit" - exits the program.



* Weights file is a list of numbers for the weights of each layer seperated by a space or new line. The weights go from the highest energy to the lowest. The decimal seperator is a point not a comma.


* example input file:
"
setVariables
200
100
100
100
7
10
1000
1
readWeights
weights.txt
writeFile
exit
"

* example weights file:
"
1
0.80
0.295
0.25
0.192
0.165
0.146
0.131
0.119
0.110
0.102
0.0954
0.0896
0.0845
0.0799
0.0759
0.0720
0.0679
0.0644
0.0614
0.0592
0.0491
"

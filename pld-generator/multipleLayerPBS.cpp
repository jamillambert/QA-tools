//============================================================================
// Program name : multipleLayerPBS.cpp
// Authors      : Jamil Lambert, Dagmar Sch�nenberg 2013
// Version      : 2.1
// Description  : writes a *.pld file for a multiple layer PBS beam
//============================================================================

#include <iostream>
#include <iomanip>
#include <fstream>
#include <cmath>
#include <vector>
#include <sstream>
#include <stdlib.h>
#include <string.h>
#include <windows.h>

using namespace std;

double range;
int noLayers;
double spotSpacing;		// in mm
double layerSpacing;	// in mm
double fieldSizeX;		// in mm
double fieldSizeY;		// in mm
double modWidth;		// in mm
double maxEnergy;		//in MeV
double totalMU;
int noSpots;
int noSpotsX;
int noSpotsY;
int noPaintings;
vector<double> layerWeight;
vector<double> layerMeterSet;
string outfilename;
bool disp;


static bool printVariables() {
/*
* Variables print to screen
*/
	cout << "\nRange set to: " << range << "mm";
	cout << "\nMax Energy set to: " << maxEnergy << "MeV";
	cout << "\nField size set to: " << fieldSizeX << "mm";
	cout << "\nField size set to: " << fieldSizeY << "mm";
	cout << "\nModulation width set to: " << modWidth << "mm";
	cout << "\nSpot spacing set to: " << spotSpacing << "mm";
	cout << "\nLayer spacing set to: " << layerSpacing << "mm";
	cout << "\nNumer of Layers: " << noLayers;
	cout << "\nNumer of Spots: " << noSpots;
	cout << "\nTotal MU set to: " << totalMU << "MU";
	cout << "\nMU per spot set to: " << totalMU/noSpots << "MU";
	return true;
}


static bool setVariables(istream& sourceStream) {
/*
* Variables can be changed here, entering 'd' sets the default value
*/
	double enteredNum;
    string enteredVal;
	if(!sourceStream) {
		sourceStream.clear();
		sourceStream >> enteredVal;
 	}

	if (disp) cout << "\nEnter max Range (0-320mm) (Enter d for default, s to skip): ";
	sourceStream >> enteredNum;
	if(!sourceStream){
		sourceStream.clear();
		sourceStream >> enteredVal;
		if(enteredVal == "s" && range > 0 && range < 320)
             cout << "Range not changed: " << range << "mm\n";
        else if (enteredVal == "setVariables") {
             return setVariables(sourceStream);
        }
        else {
             cout << "\nRange set to default: 200mm \n";
             range = 200.0;
        }
	}
	else if(enteredNum <= 0 || enteredNum > 320) {
		cout << "\nRange " << enteredNum << "mm outside limits, set to default: 200mm \n";
		range = 200.0;
    }
    else range = enteredNum;

	if (disp) cout << "\nEnter Field size in x (max 300mm): ";
	sourceStream >> enteredNum;
	if(!sourceStream){
		sourceStream.clear();
		sourceStream >> enteredVal;
		if(enteredVal == "s" && fieldSizeX > 0 && fieldSizeX <= 300)
             cout << "Field size not changed: " << fieldSizeX << "mm\n";
        else {
             cout << "\nField size in x set to default: 100mm \n";
             fieldSizeX = 100.0;
        }
	}
	else if(enteredNum < 0 || enteredNum > 300) {
		cout << "\nField Size X " << enteredNum << "mm outside limits, set to default: 100mm \n";
		fieldSizeX = 100.0;
    }
    else fieldSizeX = enteredNum;

	if (disp) cout << "\nEnter Field size in y (max 400mm): ";
	sourceStream >> enteredNum;
	if(!sourceStream){
		sourceStream.clear();
		sourceStream >> enteredVal;
		if(enteredVal == "s" && fieldSizeY > 0 && fieldSizeY <= 400)
             cout << "Field size not changed: " << fieldSizeY << "mm\n";
        else {
             cout << "\nField size in y set to default: 100mm\n";
             fieldSizeY = 100.0;
        }
	}
	else if(enteredNum < 0 || enteredNum > 400) {
		cout << "\nField Size Y " << enteredNum << "mm outside limits, set to default: 100mm\n";
		fieldSizeY = 100.0;
    }
    else fieldSizeY = enteredNum;


	if (disp) cout << "\nEnter SOBP width in (in mm, 0 for single layer): ";
	sourceStream >> enteredNum;
	if(!sourceStream){
		sourceStream.clear();
		sourceStream >> enteredVal;
		if(enteredVal == "s" && modWidth <= range && modWidth >= 0)
             cout << "Modulation not changed: " << modWidth << "mm\n";
        else {
		     cout << "\nModulation set to: " << modWidth << "mm\n";
        }
	}
	else if(enteredNum > range || enteredNum < 0) {
         if (range < 100) modWidth = range;
         else modWidth = 100;
         cout << "\nModulation " << enteredNum << "mm outside limits, set to default: " << modWidth <<"mm\n";
    }
    else modWidth = enteredNum;

	if (disp) cout << "\nEnter spot spacing (1-50mm): ";
	sourceStream >> enteredNum;
	if(!sourceStream){
		sourceStream.clear();
		sourceStream >> enteredVal;
		if(enteredVal == "s" && spotSpacing >= 1 && spotSpacing <= 50)
             cout << "Spot spacing not changed: " << spotSpacing << "mm\n";
        else {
		     cout << "\nSpot spacing set to: " << spotSpacing << "mm\n";
        }
	}
	else if(enteredNum > 50 || enteredNum < 1) {
         cout << "\nSpot spacing " << enteredNum << "mm outside limits, set to default: 10mm\n";
         spotSpacing = 10;
    }
    else spotSpacing = enteredNum;

	if (disp) cout << "\nEnter layer spacing (1-50mm): ";
	sourceStream >> enteredNum;
	if(!sourceStream){
		sourceStream.clear();
		sourceStream >> enteredVal;
		if(enteredVal == "s" && layerSpacing >= 1 && layerSpacing <= 50)
             cout << "Layer spacing not changed: " << layerSpacing << "mm\n";
        else {
		     cout << "\nLayer spacing set to: " << layerSpacing << "mm\n";
        }
	}
	else if(enteredNum > 50 || enteredNum < 1) {
         cout << "\nLayer spacing " << enteredNum << "mm outside limits, set to default: 10mm\n";
         layerSpacing = 10;
    }
    else layerSpacing = enteredNum;

	if (modWidth == 0)
		noLayers = 1;
	else
		 noLayers = (int)((modWidth+layerSpacing)/layerSpacing + 0.5);
	while(noLayers*layerSpacing > range)
		noLayers--;
	noSpotsX = (int)(fieldSizeX / spotSpacing)+1;
	noSpotsY = (int)(fieldSizeY / spotSpacing)+1;
	noSpots = noLayers * noSpotsX * noSpotsY;

	if (disp) cout << "\nEnter total number of MU: " ;
	sourceStream >> enteredNum;
	if(!sourceStream){
		sourceStream.clear();
		sourceStream >> enteredVal;
		if(enteredVal == "s" && totalMU >= noSpots*0.01 && totalMU/noSpots <= 12)
             cout << "Total MU not changed: " << totalMU << " MU\n";
        else {
             totalMU = noSpots;
		     cout << "\nTotal MU set to default: 1MU/spot = " << totalMU << " MU\n";
        }
	}
	else if(enteredNum/noSpots > 12 || enteredNum < noSpots*0.01) {
         totalMU = noSpots;
         cout << "\nEntered MU " << enteredNum << "MU outside limits, set to default 1MU per spot = " << totalMU << " MU\n";
    }
    else totalMU = enteredNum;

	if (disp) cout << "\nEnter number of paintings (default 1): ";
	sourceStream >> noPaintings;
	if(!sourceStream || noPaintings < 1 || noPaintings > 50) {
		cout << "\nNumber of paintings set to default: 1\n";
		noPaintings = 1;
	}

	maxEnergy = 30.883 * pow(range / 10, 0.5741);  //  Formel WPE
	return true;
}

static bool readWeights() {
	/*
	*   Reads in the layer weights from a file
	*   weights are a list of number seperated by a space or line break
	*   with no other characters in the file.
	*/
	vector<double> newWeights(noLayers, 1);
	string fileName;
	if (disp) cout << "\nEnter file name of weights file: ";
	cin >> fileName;
	ifstream inFile ( fileName.c_str() );
	if (!inFile) {
		std::cout << "\nFile Read Error";
		return false;
	}
	else {
		for (int i = 0; i < noLayers; i++) {
		double weight;
		inFile >> weight;
		if(!inFile) {
			cout << "\nError reading weight no. " << i << ", set 0.0";
			newWeights[i] = 0.0;
		}
		else
			newWeights[i] = weight;
		}
	}
 	layerWeight = newWeights;
	vector<double> newMeterSet(noLayers, 0);
	double cumulativeMeterSet = 0;
	for (int i = 0; i < noLayers; i++) {
		cumulativeMeterSet += layerWeight[i]*noSpotsY*noSpotsX;
		newMeterSet[i] = cumulativeMeterSet;
	}
	layerMeterSet = newMeterSet;
	return true;
}

static bool setDefault() {
/*
* Sets the variables to default values of a single layer 200mm range 10x10cm field
*/
	range = 200.0;
	noLayers = 1;
	spotSpacing = 10.0;
	layerSpacing = 10.0;
	fieldSizeX = 100.0;
	fieldSizeY = 100.0;
	modWidth = 0;
	noPaintings = 1;
	noSpotsX = (int)(fieldSizeX/spotSpacing)+1;
	noSpotsY = (int)(fieldSizeY/spotSpacing)+1;
	noSpots = noLayers*(noSpotsX)*(noSpotsY);
	totalMU = noSpots;
	maxEnergy = 30.883* pow((range)/10,0.5741);  //  Formel WPE
	vector<double> newWeights(1, 1);
	vector<double> newMeterSet(1, noSpotsY*noSpotsX);
	layerWeight = newWeights;
	layerMeterSet = newMeterSet;
	return true;
}


static bool writeFile() {
/*
* Writes the configured PBS field to a .pld file in the application directory
* The variables must be set first and the weights entered before this can be run.
*/
    if (noLayers == 0) {
       cout << "\nERROR, Set variables first\n";
       return false;
    }
    if (noLayers == 1) {
		vector<double> newWeights(1, 1);
		vector<double> newMeterSet(1, noSpotsY*noSpotsX);
		layerMeterSet = newMeterSet;
		layerWeight = newWeights;
	}
	if (layerMeterSet.size() < noLayers || layerWeight.size() < noLayers) {
		cout << "\nERROR, layer weights not set correctly, defaulting to uniform layer weights\n";
		vector<double> newWeights(noLayers, 1);
        vector<double> newMeterSet(noLayers, 0);
        double cumulativeMeterSet = 0;
        layerWeight = newWeights;
        for (int i = 0; i < noLayers; i++) {
            cumulativeMeterSet += layerWeight[i]*noSpotsY*noSpotsX;
            newMeterSet[i] = cumulativeMeterSet;
        }
        layerMeterSet = newMeterSet;
	}
	double currentLayerEnergy = maxEnergy;
	double currentLayerRange = range;
	stringstream sstm;
	sstm << "PBSfield_" << maxEnergy << "MeV_" << fieldSizeX << "x" << fieldSizeY << "x"<< modWidth << "_" << totalMU<< "MU.pld";
	outfilename = sstm.str();
	ofstream outfile(outfilename.c_str());
	outfile  << fixed << setprecision(1) << "Beam,Patient ID,Patient Name,Patient Initial,Patient Firstname,Plan Label,Beam Name," << totalMU <<","<< layerMeterSet[noLayers-1]  <<","<< noLayers << "\n";
	int elementsInLayer = noSpotsX*noSpotsY*2;
	for(int i = 0; i < noLayers; i++) {
		outfile  << "Layer,Spot1," << currentLayerEnergy <<","<< layerMeterSet[i] << ","<< elementsInLayer << "," << noPaintings <<"\n";
		double spotPosY = -fieldSizeY/2;
		for (int x = 0; x < noSpotsX ; x++) {
			double spotPosX = -fieldSizeX/2;
			for (int y = 0; y < noSpotsY ; y++) {
				outfile   << "Element," << spotPosY <<","<<spotPosX << ",0,0.0\n";
				outfile  << "Element," << spotPosY <<","<<spotPosX << "," << layerWeight[i] << ",0.0"<<endl;
				spotPosX = spotPosX + spotSpacing;
			}
			spotPosY = spotPosY + spotSpacing;
		}
		currentLayerRange -= layerSpacing;
		if (currentLayerRange < 0) {
			cout << "\nError range < 0, created file invalid";
			outfile.close();
			return false;
		}
		currentLayerEnergy = 30.883* pow((currentLayerRange/10),0.5741);
	}
    if (!outfile)
        return false;
    outfile.close();
    return true;
}


int main(int argc, char *argv[]){
	if (argc == 1) {
		disp = true;
        cout << "============================================================================\n";
        cout << "Program     : multipleLayerPBS.cpp\n";
        cout << "Authors     : J. Lambert, D. Schoenenberg  2013\n";
        cout << "Version     : 2.1\n";
        cout << "Copyright   : WPE\n";
        cout << "Description : writes a *.pld file for a multiple layer PBS beam\n";
        cout << "============================================================================";
     }
	else if (argc == 2) {
		disp = false; /* Commands are run from a file no input/output during runtime */
		cout << "\nPlease wait, or type exit to exit if program is frozen\n";
	}
	else {
		cout << "\n\nUsage:\n multipleLayerPBS -n < input\n-n suppresses output of the menu";
		cout << "\n\n by  J. Lambert and D. Schoenenberg 2013";
		cout << "\nwrites a *.pld file for a defined PBS field with multiple layers each with homogeneous spot weights." << endl;
		return 1;
	}

	bool menu = true;
	while(menu) {
		/*
		* Displays the main user interface and reads in commands,
		* and executes the relevent functions, if EOF is
		* reached, the program exits.  If run from an input file
		* no output is desplayed to the terminal (disp = false), but
		* Errors are always output to the terminal
		*/
		string cmd, temp;
		if (cin.eof())
			break;
		else if (cin.fail()) {  /* If an invalid input has been entered the input buffer is cleared. */
			cin.clear();
			cin >> cmd;
		}
		else {
			if (disp){
				cout << "\n\n\n\nMAIN MENU\n\nPlease Input your option\n ";
				cout << "\n  1. Set values to default";
				cout << "\n  2. Change variables";
				cout << "\n  3. Read variables from a file";
				cout << "\n  4. Show current variable values";
				cout << "\n  5. Read layer weights from file";
//				cout << "\n  6. no function yet";
				cout << "\n  7. Output File";
				cout << "\n  8. EXIT";
				cout << "\n\nCommand (1-8) ?";
			}
			cin >> cmd;
			if (cin.eof())
				break;
			else if (cin.fail()) {
				cin.clear();
				cin >> cmd;
			}
			else if (cmd == "1" || cmd == "setDefaults") {
				if (!setDefault()) cout << "\nFailed to set defaults";
				else if (disp) cout << "\nValues set to default";
			}
			else if (cmd == "2" || cmd == "setVariables") {
				if (!setVariables(cin)) cout << "\nFailed to set variables";
				else if (disp) cout << "\nValues sucessfully set";
			}
			else if (cmd == "3" || cmd == "readFile") {
				bool oldDispValue = disp;
				if (disp) cout << "\n Enter file name: ";
				string fileName;
				cin >> fileName;
				ifstream inFile ( fileName.c_str() );
				disp = false;
				if (!inFile) cout << "\nError reading file";
				else if (!setVariables(inFile))	cout << "\nFailed to set variables";
				else if (oldDispValue) cout << "\nValues sucessfully set";
				disp = oldDispValue;
			}
			else if (cmd == "4" || cmd == "printVariables") {
				if (!printVariables()) cout << "Error, variables invalid";
			}
			else if (cmd == "5" || cmd == "readWeights"){
				if (!readWeights()) cout << "\nWeights not changed";
				else if (disp) cout << "\nWeights set from file";
			}
			else if (cmd == "6" || cmd == "notUsed") {
			}
			else if (cmd == "7" || cmd == "writeFile"){
				if (!writeFile()) cout << "\nFailed to write to file";
				else cout << "\npld file written to: " << outfilename;
			}
			else if (cmd == "8" || cmd == "exit")
				return 0;
			else
				cout << "\n\nInvalid input. " << cmd;
		}
	}
	return 0;
}

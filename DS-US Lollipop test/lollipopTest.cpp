//============================================================================
// Program name : lollipop test
// Author      : Jamil Lambert 2013
// Version      : 1.0
// Description  : Analyses the Exports from the QA3 device to test the lollipop
//                WET in GTR3 US
//============================================================================

#include <iostream>
#include <sstream>
#include <fstream>
#include <limits>
#include <vector>
#include <cmath>
#include <string.h>

using namespace std;
bool disp;
vector<string> QA3Dates, QA3Times;

double maxError = 0.5; //mm
double x, y;

double m = 2.9211; //For linear fit (y = m*x + b)
double b = -2.65;

double c1 = -0.4533; //For polynomial fit (y = c1*x*x + c2*x + c3)
double c2 = 3.801;
double c3 = -3.053;

static void resetReadings(vector< vector<double> >& QA3Readings){
    QA3Readings.clear();
    QA3Dates.clear();
    QA3Times.clear();
}

static void printHeader() {
	if (disp) { 
        cout << string(50, '\n');  
        cout << "===============================================================================\n";
        cout << "Program     : lollipop test\n";
        cout << "Author      : J. Lambert  2013\n";
        cout << "Version     : 1.0\n";
        cout << "Description : Analyses the QA3 data from the lollipop test in GTR3\n";
        cout << "===============================================================================\n";
    }
}
    
static bool readFile(istream& sourceStream, vector< vector<double> >& QA3Readings) {
    string enteredVal;
    double enteredNum;
    int columns = 118;
    int startColumn = 3;
    int noReadings = QA3Readings.size();
    
    sourceStream >> enteredVal;
	if(!sourceStream) {
		sourceStream.clear();
		sourceStream >> enteredVal;
 	}
	if(enteredVal == "MACHINE"){
    }
    else if (enteredVal == "TEMPLATE") {
        startColumn--;
    }
    else 
        return false;
    sourceStream.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
    for (int i = 0; sourceStream; i++) {
        vector<double> newReadings;
        for (int j = 0; j < startColumn; j++)
            sourceStream.ignore(std::numeric_limits<std::streamsize>::max(), '\t');
        sourceStream >> enteredVal;
    	if(!sourceStream) {
            sourceStream.clear();
            break;;
        }
        QA3Dates.push_back(enteredVal);      
        sourceStream >> enteredVal;
    	if(!sourceStream) {
            sourceStream.clear();
            break;
        }
        QA3Times.push_back(enteredVal);
        for (int j = 0; j < columns; j++) {
            sourceStream >> enteredNum;
        	if(!sourceStream) {
                sourceStream.clear();
                break;
            }
            newReadings.push_back(enteredNum);
        }
        if (newReadings[12] < 100) {
            printHeader();
            cout << "\nError, C_Counts too low: '" << newReadings[12] << "' on line " << i+2 << "\n";
            if (disp) {
                cout << "\n\n Press Enter to continue.\n";
                cin.ignore();
                cin.ignore();
            }
        }
        else {
            QA3Readings.push_back(newReadings);       
        }       
        sourceStream.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
    }
    if (QA3Readings.size() == noReadings) {
        printHeader();
        cout << "\nNo Readings input, ensure that the decimal separator is a . not ,\n"; 
        if (disp) {
            cout << "\n\n Press Enter to continue.\n";
            cin.ignore();
            cin.ignore();
        }
        return false;
    }
    if (QA3Readings.size() == noReadings+1) {
        printHeader();
        cout << "\nOnly one valid reading, a reading with both lollipops in and out is required ,\n"; 
        if (disp) {
            cout << "\n\n Press Enter to continue.\n";
            cin.ignore();
            cin.ignore();
        }
        return false;
    }  
	return true;
}

static void calculateRatios(vector< vector<double> >& QA3Readings) {
    int order = 0;
    double ratioLollipop;
    double ratioR20M10;
    for (int i = 0; i < QA3Readings.size()-1; i=i+2) {
        if (QA3Readings[i][12] < QA3Readings[i+1][12])
            order = 1;
        else
            order = 0;
        ratioLollipop = QA3Readings[i+order][17] / QA3Readings[i+order][18] +
                        QA3Readings[i+order][19] / QA3Readings[i+order][20];
        
        ratioR20M10 = QA3Readings[i+1-order][17] / QA3Readings[i+1-order][18] +
                      QA3Readings[i+1-order][19] / QA3Readings[i+1-order][20];
        x = ratioLollipop/ratioR20M10;
        y = m * x + b;
        QA3Readings[i].push_back(y);
        y = c1*x*x + c2*x + c3;
        QA3Readings[i+1].push_back(y);      
          
//cout << "\nC:  "   << QA3Readings[i+order][12] << "\n"; //lollipop
//cout << "\netl:  " << QA3Readings[i+order][17] << "\n";
//cout << "\netr:  " << QA3Readings[i+order][18] << "\n";
//cout << "\nebr:  " << QA3Readings[i+order][19] << "\n";
//cout << "\nebl:  " << QA3Readings[i+order][20] << "\n\n";
//cout << "\nC:  "   << QA3Readings[i+1-order][12] << "\n"; //R20M10
//cout << "\netl:  " << QA3Readings[i+1-order][17] << "\n";
//cout << "\netr:  " << QA3Readings[i+1-order][18] << "\n";
//cout << "\nebr:  " << QA3Readings[i+1-order][19] << "\n";
//cout << "\nebl:  " << QA3Readings[i+1-order][20] << "\n\n";
//cout << "\nratioLollipop:  " << ratioLollipop << "\n";
//cout << "\nratioR20M10:  " << ratioR20M10 << "\n\n"; 
//cout << "\nratio:  " << QA3Readings[i+order][118] << "\n\n";   
//cout << "\ni:  " << i << "\n";
    }
}


int main(int argc, char *argv[]){
    vector< vector<double> > QA3Baseline;
    vector< vector<double> > QA3Readings;
    
	if (argc == 1) 
		disp = true;
	else if (argc == 2) {
		disp = true;
		printHeader();
		disp = false; /* Commands are run from a file no menu input/output during runtime */
	}
	else {
		cout << "\n\nUsage:\n lollipopTest -n < input\n-n suppresses output of the menu"<< endl;
		return 1;
	}

	string baselineFileName;
    baselineFileName = "baseline.txt";
	ifstream baselineFile ( baselineFileName.c_str() );
	if (!baselineFile){
        cout << "\nError reading baseline file:" << baselineFileName << "\n\n";
        return 1;
    }
	else if (!readFile(baselineFile, QA3Baseline)) {
        cout << "\nFailed to set baseline values";
    }
    else
        calculateRatios(QA3Baseline);	

	bool menu = true;
    printHeader();
    
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
				cout << "\n\nMAIN MENU\n\nPlease Input your option\n ";
				cout << "\n  1. Read QA3 measurements export file";
				cout << "\n  2. Reset readings";
				cout << "\n  3. Calculate lollipop range error";
				cout << "\n  4. EXIT";
				cout << "\n\nCommand (1-4) ?";
			}
			cin >> cmd;
			if (cin.eof())
				break;
			else if (cin.fail()) {
				cin.clear();
				cin >> cmd;
			}
			
			else if (cmd == "1" || cmd == "readFile") {
				if (disp) {
                    cout << "\n Input file must be in sets of 2, one is with all lollipops in and the thinner\n";
                    cout << " compensator the other is all lollipops out with the thicker compensator\n";
                    cout << "\n Enter file name: ";
                }
				string fileName;
				cin >> fileName;
				ifstream inFile ( fileName.c_str() );
				if (!inFile){
                    printHeader();
                    cout << "\n    Error reading file: " << fileName;
                }
				else if (!readFile(inFile, QA3Readings)) {
                    printHeader();
                    cout << "\n    Failed to read QA3 measurements";
                }
                else if (disp) {
                    printHeader();
                    cout << "\n    Measurements successfully read";
                }
			}
			
			else if (cmd == "2" || cmd == "reset") {
				resetReadings(QA3Readings);
                if (disp) {
                    printHeader();
				    cout << "\n    Readings reset";
                }
				QA3Baseline.clear();
                baselineFile.clear();
                baselineFile.seekg(0, ios::beg);
                if (!baselineFile) {
                    printHeader();
                    cout << "\nError reading baseline file:" << baselineFileName;
                }
                else if (!readFile(baselineFile, QA3Baseline)) {
                    printHeader();
                    cout << "\nFailed to set baseline values";
                }
                else
                    calculateRatios(QA3Baseline);	
			}
			
			else if (cmd == "3" || cmd == "calculate") {
                if (QA3Readings.size() == 0) {                   
                    printHeader();
                    cout <<"\n    Error no measurements found";
                }
				else {
                    calculateRatios(QA3Readings);
                    printHeader();
                    cout << "\n\nCalibration Date:  " << QA3Dates[0] << "\n";
                    cout.precision(2);
                    for (int i = 0; i < QA3Readings.size()-1; i=i+2) {
                        double errorLinear = QA3Readings[i][118] - QA3Baseline[0][118];
                        double errorPoly = QA3Readings[i+1][118] - QA3Baseline[1][118];
                        cout << "\nDate: " << QA3Dates[i+2] << "  Time: " << QA3Times[i+2] << "  Range error: " << errorPoly << "mm  ";
                        if (abs(errorPoly) < maxError)
                            cout << "Pass";
                        else
                            cout << "FAIL!";
                    }
                    if (disp){
                        cout <<"\n\n\nPress Enter to continue.\n";
                        cin.ignore();
                        cin.ignore();                  
                        printHeader();
                    }
                    else
                        cout << "\n\n";
                }
			}
			
			else if (cmd == "4" || cmd == "exit")
				return 0;
			else
				cout << "\n\n    Invalid input: " << cmd;
		}
	}
	return 0;
}

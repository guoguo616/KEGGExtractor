#include <opencv2/opencv.hpp>
#include <iostream>
#include <string>
#include <sys/stat.h>
#include <fstream>

using namespace std;
using namespace cv;

#define WHITE 255
#define BLACK 0

inline bool file_exists(const string& name) {
	struct stat buffer;
	return (stat(name.c_str(), &buffer) == 0);
}

string trim(string s) {
	if (s.empty()) {
		return s;
	}
	s.erase(0, s.find_first_not_of(" "));
	s.erase(s.find_last_not_of(" ") + 1);
	return s;
}

string rtrim(string s) {
	if (s.empty()) {
		return s;
	}
	s.erase(s.find_last_not_of(" ") + 1);
	return s;
}

vector<string> split(string s, char c='#') {
	vector<string> split_str;
	int last_pos = 0;
	for (int i = 0; i < s.length(); i++) {
		if (s[i] == c) {
			if (i - last_pos > 0) {
				split_str.push_back(s.substr(last_pos, i - last_pos));
			}
			last_pos = i + 1;
		}
	}
	if (last_pos < s.length()) {
		split_str.push_back(s.substr(last_pos, s.length() - last_pos));
	}
	return split_str;
}

Mat preProcess(Mat& img) {
	Mat black, red, black_or_red;
	inRange(img, Scalar(0, 0, 0), Scalar(0, 0, 0), black);

	inRange(img, Scalar(0, 0, 255), Scalar(0, 0, 255), red);
	bitwise_or(black, red, black_or_red);
	return black_or_red;
}

void display(Mat& img) {
	imwrite("image.png", img);
	waitKey(0);
}

void matchRectangle(Mat& img, int width, int height, int mismatch, vector<Point>& rectanglesFound) {
	int match_count;
	for (int y = 0; y <= img.rows - height; y++) {
		for (int x = 0; x <= img.cols - width; x++) {
			match_count = 0;
			for (int w = 0; w < width; w++) {
				if (img.at<uchar>(Point(x + w, y)) != WHITE || img.at<uchar>(Point(x + w, y + height - 1)) != WHITE)
					break;
				else 
					match_count++;
			}
			if (match_count + mismatch < width)
				continue;
			match_count = 0;
			for (int h = 0; h < height; h++) {
				if (img.at<uchar>(Point(x, y + h)) != WHITE || img.at<uchar>(Point(x + width - 1, y + h)) != WHITE)
					break;
				else
					match_count++;
			}
			if (match_count + mismatch >= height) {
				rectanglesFound.push_back(Point(x, y));
			}
		}
	}
}

void drawRectangles(Mat& img, int width, int height, vector<Point>& rects) {
	for (int i = 0; i < rects.size(); i++) {
		Point p = rects[i];
		rectangle(img, p, Point(p.x + width - 1, p.y + height - 1), Scalar(0,0,255), 1);
	}
}

struct Letter {
	string name;
	vector<string> pixels;
	int w = 0, h, max_exclusive = 0;

	Letter(string _name, vector<string> _pixels) {
		name = _name, pixels = _pixels;
		for (int i = 0; i < _pixels.size(); i++) {
			w = max(w, (int)_pixels[i].length());
			for (int j = 0; j < _pixels[i].length(); j++) {
				if (_pixels[i][j] == ',') { max_exclusive++; }
			}
		}
		h = _pixels.size();
		max_exclusive = max(max_exclusive, 1);
	}

	bool match(Mat& img, int x, int y) {
		// try to match THIS letter at THIS coordinate.
		bool found = true;
		int excl_cnt = 0;
		for (int i = 0; i < h; i++) {
			for (int j = 0; j < pixels[i].size(); j++) {
				char p = pixels[i][j];
				if (p == ' ') continue;
				else if (p == 'o') {
					if (img.at<uchar>(Point(x + j, y + i)) != WHITE) {
						found = false;
						break;
					}
				}
				else if (p == '.') {
					if (img.at<uchar>(Point(x + j, y + i)) == WHITE) {
						found = false;
						break;
					}
				}
				else if (p == ',') {
					if (img.at<uchar>(Point(x + j, y + i)) == WHITE) { 
						excl_cnt++; 
					}
				}
			}
			if (!found) { break; }
		}
		if (found && excl_cnt < max_exclusive) 
			return true; 
		else 
			return false;
	}
};

void loadLetters(string path, vector<Letter>& letters) {
	ifstream pixel_in(path);
	string l, name;
	vector<string> letter_pixels;
	bool reading = false;
	while (getline(pixel_in, l)) {
		if (l.size() == 0 || l[0] == '#') { continue; }
		if (l[0] == '>') {
			vector<string> split_str = split(l.substr(1, l.length() - 1));
			if (split_str.size() == 0) { cout << "WRONG LETTER DATABASE"; }
			if (reading) {
				letters.push_back(Letter(name, letter_pixels));
				letter_pixels.clear();
			}
			reading = true;
			name = trim(split_str[0]);
		}
		else{
			letter_pixels.push_back(l);
		}
	}
	pixel_in.close();
}

void matchLetter(Mat& img, vector<Letter>& letters, vector<vector<Point>>& found_at) {
	for (int i = 0; i < letters.size(); i++) {
		Letter l = letters[i];
		cout << l.name << endl;
		vector<Point> points;
		for (int y = 0; y < img.rows - l.h; y++) {
			for (int x = 0; x < img.cols - l.w; x++) {
				if (l.match(img, x, y)){
					points.push_back(Point(x, y));
				}
			}
		}
		found_at.push_back(points);
	}
}

void dump(string path, vector<Point>& rectsFound, int rectW, int rectH, vector<Letter>& letters, vector<vector<Point>> lettersFoundAt) {
	ofstream out_file(path);
	for (int i = 0; i < rectsFound.size(); i++) {
		out_file << "rect\t" << rectsFound[i].x << "," << rectsFound[i].y << "\t" << rectW << "\t" << rectH << endl;
	}
	for (int i = 0; i < letters.size(); i++) {
		out_file << "char\t" << letters[i].name;
		for (int j = 0; j < lettersFoundAt[i].size(); j++){
			Point p = lettersFoundAt[i][j];
			out_file << "\t" << p.x << "," << p.y;
		}
		out_file << endl;
	}
	out_file.close();
}

int main(int argc,char **argv){
	string testcaseDir = "./";
	//hsa05215
	string file_path = testcaseDir+argv[1];
	if (!file_exists(file_path)) { cout << "file not exist." << endl; return 1; }
	Mat img = imread(file_path);
	Mat clean_img = preProcess(img);
	vector<Letter> letters;
	vector<Point> rectFound;
	vector<vector<Point>> lettersFoundAt;
	
	loadLetters(testcaseDir + "letters_by_pixel.txt", letters);
	/*for (int i = 0; i < letters.size(); i++) {
		Letter le = letters[i];
		cout << le.name << " " << le.h << " " << le.w << " " << le.max_exclusive << endl;
		for (int j = 0; j < le.pixels.size(); j++) {
			cout << le.pixels[j] << endl;
		}
	}*/
	matchLetter(clean_img, letters, lettersFoundAt);
	for (int i = 0; i < lettersFoundAt.size(); i++) {
		Letter le = letters[i];
		cout << le.name << " " << lettersFoundAt[i].size() << endl;
		drawRectangles(img, le.w, le.h, lettersFoundAt[i]);
		//display(img);
	}
	matchRectangle(clean_img, 47, 18, 0, rectFound);
	matchRectangle(clean_img, 48, 17, 0, rectFound);
	drawRectangles(img, 47, 18, rectFound);
	display(img);
	dump(file_path + ".nodes.txt", rectFound, 47, 18, letters, lettersFoundAt);
	
	return 0;
}

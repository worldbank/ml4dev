all:
	@echo See Makefile for options

step1:
	# Builds the data/elements.json file
	python 01_get_elements.py

step2:
	# Print some stats
	python 02_get_stats.py

step3:
	# Builds the data/ways.json file
	python 03_build_ways_data.py

step4:
	# Downloads 10 sample photos of the top 10 sports
	python 04_download_satellite.py --sport baseball --count 10
	python 04_download_satellite.py --sport tennis --count 10
	python 04_download_satellite.py --sport soccer --count 10
	python 04_download_satellite.py --sport basketball --count 10
	python 04_download_satellite.py --sport unknown --count 10
	python 04_download_satellite.py --sport golf --count 10
	python 04_download_satellite.py --sport american_football --count 10
	python 04_download_satellite.py --sport volleyball --count 10
	python 04_download_satellite.py --sport multi --count 10
	python 04_download_satellite.py --sport softball --count 10
	# mv satellite/*png satellite/training/
	# mv satellite/*png satellite/testing/

step5:
	# Draw the bbox on the test files
	python 05_draw_bbox.py

step6:
	# Get some random images
	python 06_get_negatives.py --count 25
	find satellite/negative -type f > negative.txt

createsamples:
	opencv_createsamples -info info_baseball.dat -num 99 -vec info_baseball.vec
	opencv_createsamples -info info_basketball.dat -num 100 -vec info_basketball.vec
	opencv_createsamples -info info_tennis.dat -num 9998 -vec info_tennis.vec
	opencv_traincascade -data output -vec info_baseball.vec -bg negative.txt -numPos 99 -numNeg 100
	opencv_traincascade -data output -vec info_basketball.vec -bg negative.txt -numPos 100 -numNeg 100
	opencv_traincascade -data output -vec info_tennis.vec -bg negative.txt -numPos 9998 -numNeg 5000


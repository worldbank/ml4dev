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

step5:
	# Draw the bbox on the test files
	python 05_draw_bbox.py

step6:
	# Get some random images
	python 06_get_negatives.py --count 25

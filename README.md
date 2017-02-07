<span>[DRAFT] Machine Learning for Development: </span>

<span>A method to Learn and Identify Earth Features from Satellite Images</span>

<span>Prepared by Antonio Zugaldia; commissioned by the Big Data team, Innovation Labs, the World Bank</span>

<span>All code is MIT licensed, and the text content is CC-BY. Please feel free to send edits and updates via Pull Requests.</span>

<span>Foreword</span>
=====================

“Machine Learning” is one of the tools on Big Data analysis. The need to process large amounts of data has contributed to accelerate the tools and application of new vastly scalable processing techniques. In this report we aim to facilitate the adoption of machine learning techniques to development outputs and outcomes. </span>

<span>In this particular case we aim to detect automatically distinct features such as playgrounds from standard aerial images, </span><span>as a milestone towards automatic detection of more refined applications like paved (or not) roads, dams, schools, hospitals, non-formal settlements, wells, different stages on agricultural crops, ...</span>

<span></span>

<span>Introduction</span>
=========================

<span>In this document we describe a complete methodology to detect earth features in satellite images using OpenCV, an open source computer vision and machine learning software. We describe the step by step process using documented Python software, and analyze potential ways of improving it. Finally, we review how to extend this analysis to an Apache Spark cluster hosted on AWS, and some recent developments on Google’s cloud offering. </span><span>These tools can be used to analyze and visualize all kinds of data, including Sustainable Development Goals (SDG) data.</span><sup>[\[b\]](#cmnt2)</sup>

<span></span>

<span>Computer Visions meets Machine Learning</span>
====================================================

<span></span>

<span>Machine learning</span><sup>[\[1\]](#ftnt1)</sup><span> “</span><span class="c25">explores the construction and study of algorithms that can learn from and make predictions on data. Such algorithms operate by building a model from example inputs in order to make data-driven predictions or decisions, rather than following strictly static program instructions.</span><span>”</span>

<span></span>

<span>Those inputs, or features, are at the core of any machine learning flow. For example, when doing a supervised regression those inputs are numbers, or when doing some document classification, we use a bag of words (</span><span class="c11">where grammar is ignored or even word order but word multiplicity is kept).</span>

<span class="c11"></span>

<span class="c11">However, when it comes to analyzing images, we cannot simply use the binary representation of every pixel as input. Not only this is inefficient from a memory handling perspective, raw pixels do not provide an useful representation of the content of an image, its shapes, corners, edges.</span>

<span class="c11"></span>

<span class="c11">This is where Computer Vision plays a key role, extracting features from an image in order to be able to provide a useful input for machine learning algorithms. As there are many possibilities for extracting these features from images, in the following pages we are going to describe one well suited for our perspective, a cascade classifier using the open source tool OpenCV</span><sup>[\[2\]](#ftnt2)</sup><span class="c11">.</span>

<span class="c11"></span>

<span>Methodology</span>
------------------------

<span class="c11"></span>

<span class="c11">Our goal is to be able to identify specific features from a satellite image. In other words, we need to train a supervised classification model with some input images in order to be able to predict the existence and location of that element in other satellite images.</span>

<span class="c11"></span>

<span class="c11">There are many ways to accomplish. In this document we use OpenCV (Open Source Computer Vision Library), which is able to bring significant results as we will show later. OpenCV was originally developed by Intel Corporation and is an open source computer vision and machine learning software library widely adopted by the industry. It comes with a large number of algorithms and tools that serve our purpose.</span>

<span class="c11"></span>

<span class="c11">We are going to focus on the cascade classifier, which has two major stages: training and detection</span><sup>[\[3\]](#ftnt3)</sup><span class="c11">.</span>

<span class="c11"></span>

### <span>Training</span>

<span class="c11"></span>

<span class="c11">In order to train a high quality classifier we need a large number of high quality input images. For the purpose of this research, we are going to use 10,000 images acquired from the Mapbox service</span><sup>[\[4\]](#ftnt4)</sup><span class="c11"> using the author’s subscription to the service. Please note that these images were only used for the purpose of this research and were never released to a larger audience.</span>

<span class="c11"></span>

<span class="c11">The information about the actual geographic location of the features was obtained from OSM (</span><span class="c11">OpenStreetMap</span><span class="c11">). In the following pages we describe the process in detail.</span>

<span class="c11"></span>

<span class="c11">All the source code mentioned in these pages is available in the GitHub repository mentioned in the references section at the end of this document. All these commands were run in a 32-CPU virtual machine running Ubuntu Linux </span><span class="c11">on Google’s Cloud</span><sup>[\[c\]](#cmnt3)</sup><span class="c11"> (type: </span><span class="c5">n1-highcpu-32</span><span class="c11">).</span>

<span class="c11"></span>

#### <span>Step 1: Obtain the location of the elements</span>

<span class="c11"></span>

<span class="c11">For this research, we have chosen a feature that is easily identifiable from space with abundant information in the OSM database: a tennis court. More importantly, we have chosen a feature and methodology that can be then adapted to any other features in the OSM database. Our goal is to create a flow useful for Development.</span>

<span class="c11"></span>

<span class="c11">The first thing we did was to download the location of every pitch in the US available in OSM. These are technically defined by OSM by the </span><span class="c5">leisure=pitch</span><span class="c11"> key/value. to automate this process we built a simple Python client to the Overpass API</span><sup>[\[5\]](#ftnt5)</sup><span class="c11">.</span>

<span class="c11"></span>

<span class="c11">The query is as follows (the cryptic </span><span class="c5">(.\_;&gt;;);</span><sup>[\[d\]](#cmnt4)</sup><span class="c5"> </span><span class="c11">asks for the nodes and ways that are referred by the relations and ways in the result):</span>

<span class="c11"></span>

<span class="c5">\[out:json\];</span>

<span class="c5">way</span>

<span class="c5">  \[leisure=pitch\]</span>

<span class="c5">  ({query\_bb\_s},{query\_bb\_w},{query\_bb\_n},{query\_bb\_e});</span>

<span class="c5">(.\_;&gt;;);</span>

<span class="c5">out;</span>

<span class="c11"></span>

<span class="c11">Where the </span><span class="c5">{query\_bb\_s},{query\_bb\_w},{query\_bb\_n},{query\_bb\_e}</span><span class="c11"> parameters indicate the bounding box for the US</span><sup>[\[6\]](#ftnt6)</sup><span class="c11">. Because querying for every pitch in the US is too big of a query (which will make the Overpass API server to timeout), we divided the US in 100 sub-bounding boxes. This is implemented in the </span><span class="c5">01\_get\_elements.py</span><span class="c11"> file.</span>

<span class="c11"></span>

<span class="c11">This data contains </span><span class="c11">1,265,357 nodes and 170,070 ways, an average of about 7.5 nodes per way</span><sup>[\[e\]](#cmnt5)[\[f\]](#cmnt6)</sup><span class="c11">. A sample node looks like:</span>

<span class="c11"></span>

<span class="c5">{"lat": 27.1460817, "lon": -114.293208, "type": "node", "id": 3070587853}</span>

<span class="c11"></span>

<span class="c11">And a way looks like:</span>

<span class="c11"></span>

<span class="c5">{"nodes": \[1860795336, 1860795357, 1860795382, 1860795346, 1860795336\], "type": "way", "id": 175502416, "tags": {"sport": "basketball", "leisure": "pitch"}}</span>

<span class="c11"></span>

<span class="c11">We cached the results to avoid unnecessary further queries to the server. </span>

<span class="c11"></span>

#### <span>Step 2: Statistics</span>

<span class="c11"></span>

<span class="c11">Once we had the data, we ran some sample statistics to see how many potential elements we had available for the US. The result is as follow, and the code is available on </span><span class="c5">02\_get\_stats.py</span><span class="c11">.</span>

<span class="c11"></span>

<span class="c11">Top 10 pitches types in the US according to OSM:</span>

1.  <span class="c11">Baseball = 61,573 ways</span>
2.  <span class="c11">Tennis = 38,482 ways</span>
3.  <span class="c11">Soccer = 19,129 ways</span>
4.  <span class="c11">Basketball = 15,797 ways</span>
5.  <span class="c11">Unknown = 11,914 ways</span>
6.  <span class="c11">Golf = 6,826 ways</span>
7.  <span class="c11">American football = 6,266 ways</span>
8.  <span class="c11">Volleyball = 2,127 ways</span>
9.  <span class="c11">Multi = 1,423 ways</span>
10. <span class="c11">Softball = 695 ways</span>

<span class="c11"></span>

<span class="c11">As we can see, we have 38,482 pitches identified in OSM as a way in the US. This will be our pool of data to train the system. The importance of having this elements tagged as ways (and not just nodes) will be shown later.</span>

<span class="c11"></span>

#### <span>Step 3: Build ways data</span>

<span class="c11"></span>

<span class="c11">Next, for every way that we are interested in, we computed its centroid and its bounding box. The result is like the following and the code is in </span><span class="c5">03\_build\_ways\_data.py</span><span class="c11">:</span>

<span class="c11"></span>

<span class="c5">"201850880": {"lat": 48.38813308204558, "lon": -123.68852695545081, "bounds": \[48.3880748, -123.6886191, 48.3881912, -123.6884365\]}</span>

<span class="c11"></span>

<span class="c11">Where </span><span class="c5">201850880</span><span class="c11"> is the way ID. We use the centroid as the point where we will download the satellite imagery, and we will use the bounding box to tell the machine learning algorithm the location within the larger image where our feature of interest is located.</span>

<span class="c11"></span>

<span class="c11">We used the Python Shapely library (</span><span class="c5">shapely.geometry.Polygon</span><span class="c11">) to compute this information.</span>

<span class="c11"></span>

#### <span>Step 4: Download satellite imagery</span>

<span class="c11"></span>

<span class="c11">Now that we know the location of all tennis courts in the US, we can go ahead and download some sample satellite imagery from Mapbox. This is implemented in a Python script that allows some arguments (</span><span class="c5">04\_download\_satellite.py</span><span class="c11">):</span>

<span class="c11"></span>

<span class="c5">04\_download\_satellite.py \[-h\] \[--sport SPORT\] \[--count COUNT\]</span>

<span class="c5"></span>

<span class="c5">optional arguments:</span>

<span class="c5">  -h, --help     show this help message and exit</span>

<span class="c5">  --sport SPORT  Sport tag, for example: baseball.</span>

<span class="c5">  --count COUNT  The total number of images to download.</span>

<span class="c5"></span>

<span class="c11">For example, to download 10,000 images of tennis courts (as we did), we would run the command as follows:</span>

<span class="c11"></span>

<span class="c5">$ python 04\_download\_satellite.py --sport tennis --count 10000</span>

<span class="c11"></span>

<span class="c11">The images were downloaded at maximum resolution (1280x1280) in PNG format. Also, to make sure we did not introduce a bias, we randomized the list of ways before downloading the actual imagery.</span>

<span class="c11"></span>

<span style="overflow: hidden; display: inline-block; margin: 0.00px 0.00px; border: 0.00px solid #000000; transform: rotate(0.00rad) translateZ(0px); -webkit-transform: rotate(0.00rad) translateZ(0px); width: 624.00px; height: 624.00px;">![pitch\_tennis\_30588350.png](readme_images/image05.jpg)</span>

<span class="c11"></span>

<span class="c11">Please note that in </span><span class="c11">some cases</span><sup>[\[g\]](#cmnt7)</sup><span class="c11"> imagery is not available in that location at that zoom level (19). Those images were identified by our script and deleted from our pool.</span>

<span class="c11"></span>

<span style="overflow: hidden; display: inline-block; margin: 0.00px 0.00px; border: 0.00px solid #000000; transform: rotate(0.00rad) translateZ(0px); -webkit-transform: rotate(0.00rad) translateZ(0px); width: 624.00px; height: 624.00px;">![empty\_satellite.png](readme_images/image00.jpg)</span>

<span class="c11"></span>

#### <span>Step 5: Build samples files</span>

<span class="c11"></span>

<span class="c11">Now, for every image in our set (10,000) we need to find the actual location of the tennis court in the image. From step 3 we have the bounding box coordinates, we need to transform this into an image pixel location, and output the result in a specific format required by OpenCV.</span>

<span class="c11"></span>

<span class="c11">The format looks like this:</span>

<span class="c11"></span>

<span class="c5">satellite/gray/pitch\_tennis\_100027097.png        1        569        457        140        365</span>

<span class="c5">satellite/gray/pitch\_tennis\_100040542.png        1        559        549        161        180</span>

<span class="c5">satellite/gray/pitch\_tennis\_100042337.png        1        464        515        350        248</span>

<span class="c5">satellite/gray/pitch\_tennis\_100075597.png        1        471        366        337        546</span>

<span class="c5">satellite/gray/pitch\_tennis\_100077768.png        1        552        551        175        176</span>

<span class="c5">satellite/gray/pitch\_tennis\_100089034.png        1        521        548        237        183</span>

<span class="c5">...</span>

<span class="c11"></span>

<span class="c11">It indicates, for example, that the image </span><span class="c5">satellite/gray/pitch\_tennis\_100027097.png</span><span class="c11"> has 1 tennis court in the box defined by the bounding rectangle (569, 457, 140, 365). In all cases, we checked that the bounding rectangle was not larger than the image dimensions (1280x1280 pixels), or too small (less than 25x25 pixels), something entirely possible if they were incorrectly labeled by the OSM editor.</span>

<span class="c11"></span>

<sup>[\[h\]](#cmnt8)</sup>

<span class="c11">Also, note that this point we converted all images to grayscale (grayscale images are assumed by OpenCV’s scripts).</span>

<span class="c11"></span>

<span class="c11">In order to convert from earth coordinates to image coordinates we used the following Python method:</span>

<span class="c11"></span>

<span class="c5">def get\_rectangle(bounds):</span>

<span class="c5">    \# This converts a latitude delta into an image delta.</span>

<span class="c5">    \# For USA, at zoom level 19, we know that we have 0.21</span>

<span class="c5">    \# meters/pixel. So, an image is showing</span>

<span class="c5">    \# about 1280 pixels \* 0.21 meters/pixel = 268.8 meters.</span>

<span class="c5">    \# On the other hand we know that at the same angle,</span>

<span class="c5">    \# a degrees in latlon is</span>

<span class="c5">    \# (https://en.wikipedia.org/wiki/Latitude):</span>

<span class="c5">    \# latitude = 111,132 m</span>

<span class="c5">    \# longitude = 78,847 m</span>

<span class="c5">    latitude\_factor  = 111132.0 / 0.21</span>

<span class="c5">    longitude\_factor = 78847.0 / 0.21</span>

<span class="c5"></span>

<span class="c5">    \# Feature size</span>

<span class="c5">    feature\_width = longitude\_factor \*</span>

<span class="c5">       math.fabs(bounds\[1\] - bounds\[3\])</span>

<span class="c5">    feature\_height = latitude\_factor \*</span>

<span class="c5">       math.fabs(bounds\[0\] - bounds\[2\])</span>

<span class="c5"></span>

<span class="c5">    \# CV params (int required)</span>

<span class="c5">    x = int((image\_width / 2) - (feature\_width / 2))</span>

<span class="c5">    y = int((image\_height / 2) - (feature\_height / 2))</span>

<span class="c5">    w = int(feature\_width)</span>

<span class="c5">    h = int(feature\_height)</span>

<span class="c5">    return x, y, w, h</span>

<span class="c11"></span>

<span class="c11">The correspondence between meters and pixel is shown in the following table (courtesy of Bruno Sánchez-Andrade Nuño):</span>

<span></span>

[](#)[](#)

<table style="width:100%;">
<colgroup>
<col width="14%" />
<col width="14%" />
<col width="14%" />
<col width="14%" />
<col width="14%" />
<col width="14%" />
<col width="14%" />
</colgroup>
<tbody>
<tr class="odd">
<td align="left"><p><span class="c0"></span></p></td>
<td align="left"><p><span class="c0">Latitude</span></p></td>
<td align="left"><p><span class="c0"></span></p></td>
<td align="left"><p><span class="c0"></span></p></td>
<td align="left"><p><span class="c0"></span></p></td>
<td align="left"><p><span class="c0"></span></p></td>
<td align="left"><p><span class="c0"></span></p></td>
</tr>
<tr class="even">
<td align="left"><p><span class="c0">Zoom level</span></p></td>
<td align="left"><p><span class="c0">0</span></p></td>
<td align="left"><p><span class="c0">15</span></p></td>
<td align="left"><p><span class="c0">30</span></p></td>
<td align="left"><p><span class="c0">45</span></p></td>
<td align="left"><p><span class="c0">60</span></p></td>
<td align="left"><p><span class="c0">75</span></p></td>
</tr>
<tr class="odd">
<td align="left"><p><span class="c0">15</span></p></td>
<td align="left"><p><span class="c13 c19">4.78</span></p></td>
<td align="left"><p><span class="c13 c19">4.61</span></p></td>
<td align="left"><p><span class="c13 c19">4.14</span></p></td>
<td align="left"><p><span class="c13 c19">3.38</span></p></td>
<td align="left"><p><span class="c13 c19">2.39</span></p></td>
<td align="left"><p><span class="c13 c19">1.24</span></p></td>
</tr>
<tr class="even">
<td align="left"><p><span class="c0">16</span></p></td>
<td align="left"><p><span class="c13 c19">2.39</span></p></td>
<td align="left"><p><span class="c13 c19">2.31</span></p></td>
<td align="left"><p><span class="c13 c19">2.07</span></p></td>
<td align="left"><p><span class="c13 c19">1.69</span></p></td>
<td align="left"><p><span class="c13 c19">1.19</span></p></td>
<td align="left"><p><span class="c13 c19">0.62</span></p></td>
</tr>
<tr class="odd">
<td align="left"><p><span class="c0">17</span></p></td>
<td align="left"><p><span class="c13 c19">1.19</span></p></td>
<td align="left"><p><span class="c13 c19">1.15</span></p></td>
<td align="left"><p><span class="c13 c19">1.03</span></p></td>
<td align="left"><p><span class="c13 c19">0.84</span></p></td>
<td align="left"><p><span class="c13 c19">0.60</span></p></td>
<td align="left"><p><span class="c13 c27">0.31</span></p></td>
</tr>
<tr class="even">
<td align="left"><p><span class="c0">18</span></p></td>
<td align="left"><p><span class="c13 c19">0.60</span></p></td>
<td align="left"><p><span class="c13 c19">0.58</span></p></td>
<td align="left"><p><span class="c13 c19">0.52</span></p></td>
<td align="left"><p><span class="c13 c27">0.42</span></p></td>
<td align="left"><p><span class="c0">0.30</span></p></td>
<td align="left"><p><span class="c0">0.15</span></p></td>
</tr>
<tr class="odd">
<td align="left"><p><span class="c0">19</span></p></td>
<td align="left"><p><span class="c0">0.30</span></p></td>
<td align="left"><p><span class="c0">0.29</span></p></td>
<td align="left"><p><span class="c0">0.26</span></p></td>
<td align="left"><p><span class="c0">0.21</span></p></td>
<td align="left"><p><span class="c0">0.15</span></p></td>
<td align="left"><p><span class="c0">0.08</span></p></td>
</tr>
<tr class="even">
<td align="left"><p><span class="c0">20</span></p></td>
<td align="left"><p><span class="c0">0.15</span></p></td>
<td align="left"><p><span class="c0">0.14</span></p></td>
<td align="left"><p><span class="c0">0.13</span></p></td>
<td align="left"><p><span class="c0">0.11</span></p></td>
<td align="left"><p><span class="c0">0.07</span></p></td>
<td align="left"><p><span class="c0">0.04</span></p></td>
</tr>
<tr class="odd">
<td align="left"><p><span class="c0"></span></p></td>
<td align="left"><p><span class="c0"></span></p></td>
<td align="left"><p><span class="c0"></span></p></td>
<td align="left"><p><span class="c0"></span></p></td>
<td align="left"><p><span class="c0"></span></p></td>
<td align="left"><p><span class="c0"></span></p></td>
<td align="left"><p><span class="c0"></span></p></td>
</tr>
<tr class="even">
<td align="left"><p><span class="c0"></span></p></td>
<td align="left"><p><span class="c0">Ecuator</span></p></td>
<td align="left"><p><span class="c0">Central America, India, North Australia, South Brazil</span></p></td>
<td align="left"><p><span class="c0">Mexico, South US, South Australia, South Africa</span></p></td>
<td align="left"><p><span class="c0">New Zealand, North US, most Europe, Tip of Argentina/Chile</span></p></td>
<td align="left"><p><span class="c0">Russia, North Europe, Canada</span></p></td>
<td align="left"><p><span class="c0">Polar bears</span></p></td>
</tr>
</tbody>
</table>

<span></span>

#### <span>Step 6: Get negatives</span>

<span class="c11"></span>

<span class="c11">A training process is incomplete if we don’t have “negatives”, that is, images used as a bad example were no features are present. To solve this we built the following script:</span>

<span class="c11"></span>

<span class="c5">python 06\_get\_negatives.py \[-h\] \[--count COUNT\]</span>

<span class="c5"></span>

<span class="c5">optional arguments:</span>

<span class="c5">  -h, --help     show this help message and exit</span>

<span class="c5">  --count COUNT  The total number of negative images to download.</span>

<span class="c11"></span>

<span class="c11">We can use it like:</span>

<span class="c11"></span>

<span class="c5">$ python 06\_get\_negatives.py --count 1000</span>

<span class="c11"></span>

<span class="c11">It basically loads some random locations with actual pitches, but moves the location by a random amount to get the features out of the image:</span>

<span class="c11"></span>

<span class="c5">target\_lat = element.get('lat') + (random.random() - 0.5)</span>

<span class="c5">target\_lon = element.get('lon') + (random.random() - 0.5)</span>

<span class="c11"></span>

<span style="overflow: hidden; display: inline-block; margin: 0.00px 0.00px; border: 0.00px solid #000000; transform: rotate(0.00rad) translateZ(0px); -webkit-transform: rotate(0.00rad) translateZ(0px); width: 624.00px; height: 624.00px;">![negative\_637533520.png](readme_images/image02.png)</span>

<span class="c11"></span>

<span class="c11">Finally, we just need to put them all in one file with the following format:</span>

<span class="c11"></span>

<span class="c5">satellite/negative/negative\_1000200409.png</span>

<span class="c5">satellite/negative/negative\_1001251446.png</span>

<span class="c5">satellite/negative/negative\_1001532469.png</span>

<span class="c5">satellite/negative/negative\_1001687068.png</span>

<span class="c5">satellite/negative/negative\_1004891593.png</span>

<span class="c5">satellite/negative/negative\_1006295843.png</span>

<span class="c5">satellite/negative/negative\_1009904689.png</span>

<span class="c5">satellite/negative/negative\_1011863337.png</span>

<span class="c5">...</span>

<span class="c11"></span>

<span class="c11">In this case we don’t need to specify a bounding rectangle as these are images with no features in it.</span>

<span class="c11"></span>

#### <span>Step 7: Actual training phase</span>

<span class="c11"></span>

<span class="c11">We are finally equipped to use OpenCV’s tools to train the cascade classifier. First we need to create a </span><span class="c5">.vec</span><span class="c11"> file using </span><span class="c5">opencv\_createsamples</span><span class="c11">:</span>

<span class="c11"></span>

<span class="c5">$ opencv\_createsamples -info info\_tennis.dat -num 10000 -vec info\_tennis.vec</span>

<span class="c11"></span>

<span class="c11">This would create the .vec file using 10,000 samples. And then, we can do the actual training with </span><span class="c5">opencv\_traincascade</span><span class="c11">:</span>

<span class="c11"></span>

<span class="c5">$ opencv\_traincascade -data output -vec info\_tennis.vec -bg negative.txt -numPos 2000 -numNeg 1000</span>

<span class="c11"></span>

<span class="c11">This instructs to use 2,000 positive images, and 1,000 negative images (the default) and write the result in the </span><span class="c5">output </span><span class="c11">folder.</span>

<span class="c11"></span>

<span class="c11">This is by far the most computing intensive step of the process. We ran it for different positive/negative values and the total time for the virtual machine ranged from a few hours (for about 2,000 positive images, default) to 5 days (for 8,000 positive images). </span>

<span class="c11"></span>

### <span>Detection</span>

<span class="c11"></span>

<span class="c11">We now have a trained classifier in the form of a XML file that OpenCV can use to detect features in our images (we provide the resulting XML in the repository). Its usage can be as simple as:</span>

<span class="c11"></span>

<span class="c5">tennis\_cascade\_file = 'output/cascade-8000-4000.xml'</span>

<span class="c5">tennis\_cascade = cv2.CascadeClassifier(tennis\_cascade\_file)</span>

<span class="c5">img = cv2.imread(filename, 0)</span>

<span class="c5">pitches = tennis\_cascade.detectMultiScale(</span>

<span class="c5">  img, minNeighbors=min\_neighbors)</span>

<span class="c11"></span>

<span class="c11">Where </span><span class="c5">filename</span><span class="c11"> represents the satellite image we want to analyze and </span><span class="c5">pitches</span><span class="c11"> contain the location (if detected) of the feature in the image.</span>

<span class="c11"></span>

#### <span>Step 8: Optimizing parameters</span>

<span class="c11"></span>

<span class="c11">However, the cascade classifier has different parameters that will affect the result of the classification. A key parameter is </span><span class="c5">minNeighbors</span><span class="c11">, a parameter specifying how many neighbors each candidate rectangle should have to retain it.</span>

<span class="c11"></span>

<span class="c11">For example</span><sup>[\[7\]](#ftnt7)</sup><span class="c11">, if we were using this methodology to identify faces in a picture, and we set the </span><span class="c5">minNeighbors</span><span class="c11"> value as zero, we would get too many false positives:</span>

<span class="c11"></span>

<span style="overflow: hidden; display: inline-block; margin: 0.00px 0.00px; border: 0.00px solid #000000; transform: rotate(0.00rad) translateZ(0px); -webkit-transform: rotate(0.00rad) translateZ(0px); width: 624.00px; height: 468.00px;">![](readme_images/image11.png)</span>

<span class="c11"></span>

<span class="c11">A larger value of </span><span class="c5">minNeighbors</span><span class="c11">, will bring a better result:</span>

<span class="c11"></span>

<span style="overflow: hidden; display: inline-block; margin: 0.00px 0.00px; border: 0.00px solid #000000; transform: rotate(0.00rad) translateZ(0px); -webkit-transform: rotate(0.00rad) translateZ(0px); width: 624.00px; height: 468.00px;">![](readme_images/image10.png)</span>

<span class="c11"></span>

<span class="c11">This is way, at this point we spent some time finding the value that brings the best results for us. A common way of approaching this situation is by defining:</span>

-   <span class="c11">True positive: “There is a tennis court, and we found one.”</span>
-   <span class="c11">False positive: “There is no tennis court, and we found one.”</span>
-   <span class="c11">True negative: “There is no tennis court, and we found none.”</span>
-   <span class="c11">False negative: “There is a tennis court, and we found none.”</span>

<span class="c11"></span>

<span class="c11">In general, we are interested in maximizing true positives and true negatives, and minimizing false positives and false negatives. It is up to us to decide to what extent we want to do this. For example, in an algorithm to detect brain tumors we might want to focus on minimizing false negatives (missing an existing tumor), while in a crowdsourced system (like it could be this one), is better to target false positives because they are easy to dismiss by a human.</span>

<span class="c11"></span>

<span class="c11">Knowing this, we obtained 100 random images with tennis courts in them, and 100 random images with no tennis courts, and we used our model to check for the existence or inexistence of a tennis court on them, calculating in every case the total number of courts identified. This is done by </span><span class="c5">07\_fit\_min\_neighbors.py</span><span class="c11"> and </span><span class="c5">08\_plot\_fit.py</span><span class="c11"> and one of the results is the following:</span>

<span class="c11"></span>

<span style="overflow: hidden; display: inline-block; margin: 0.00px 0.00px; border: 0.00px solid #000000; transform: rotate(0.00rad) translateZ(0px); -webkit-transform: rotate(0.00rad) translateZ(0px); width: 624.00px; height: 468.00px;">![cascade-4000.png](readme_images/image06.png)</span>

<span class="c11"></span>

<span class="c11">This image was computed with the 4,000 positive images and 2,000 negative images. The red lines indicates the number of pitches detected in negative images as we increase </span><span class="c5">minNeighbors</span><span class="c11">, and the blue line does the same for positive images. The goal, is to make sure that the red line falls under the value of one (green dashed line = no pitches identified) while the blue one remains above one. This seems to happen when the value </span><span class="c5">minNeighbors </span><span class="c11">of goes over 300.</span>

<span class="c11"></span>

<span class="c11">In fact, for a </span><span class="c5">minNeighbors</span><span class="c11"> value of 500, we obtain:</span>

-   <span class="c11">Percentage of true positives = </span><span class="c8">73.0%</span>
-   <span class="c11">Percentage of true negatives = </span><span class="c8">82.0%</span>

<span class="c11"></span>

<span class="c11">Which seems to indicate we are going on the right direction. Further analysis will require to compute precision (how accurate our positive predictions are) and recall (what fractions of the positives our model identified) values.</span>

<span class="c11"></span>

#### <span>Step 9: Visualizing results</span><sup>[\[i\]](#cmnt9)</sup>

<span class="c11"></span>

<span class="c11">Finally, we have built </span><span class="c5">09\_draw\_results.py</span><span class="c11"> to visualize the predictions of our model. These are some actual results on images not included in the original training set:</span>

<span class="c11"></span>

<span class="c11">True positive:</span>

<span style="overflow: hidden; display: inline-block; margin: 0.00px 0.00px; border: 0.00px solid #000000; transform: rotate(0.00rad) translateZ(0px); -webkit-transform: rotate(0.00rad) translateZ(0px); width: 624.00px; height: 624.00px;">![](readme_images/image01.png)</span>

<span class="c11"></span>

<span class="c11">False positive:</span>

<span style="overflow: hidden; display: inline-block; margin: 0.00px 0.00px; border: 0.00px solid #000000; transform: rotate(0.00rad) translateZ(0px); -webkit-transform: rotate(0.00rad) translateZ(0px); width: 624.00px; height: 624.00px;">![](readme_images/image07.png)</span>

<span class="c11"></span>

<span class="c11">True negative:</span>

<span style="overflow: hidden; display: inline-block; margin: 0.00px 0.00px; border: 0.00px solid #000000; transform: rotate(0.00rad) translateZ(0px); -webkit-transform: rotate(0.00rad) translateZ(0px); width: 624.00px; height: 624.00px;">![](readme_images/image03.png)</span>

<span class="c11"></span>

<span class="c11">False negative:</span>

<span style="overflow: hidden; display: inline-block; margin: 0.00px 0.00px; border: 0.00px solid #000000; transform: rotate(0.00rad) translateZ(0px); -webkit-transform: rotate(0.00rad) translateZ(0px); width: 624.00px; height: 624.00px;">![](readme_images/image12.png)</span>

<span class="c11"></span>

#### <span>Next steps</span>

<span class="c11"></span>

<span class="c11">As we have shown until now, the cascade classifier is producing solid results over our training dataset, however, not all features in the world are as identifiable as a tennis court (a specific type of building, for example), or as available in the OSM database (low interest objects, or very recent ones after a natural disaster, for example).</span>

<span class="c11"></span>

<span class="c11">Because of these challenges, there are a number of improvements that still could be explored. Namely:</span>

-   <span class="c11 c25">Train the model with a larger dataset</span><span class="c11">: We have used thousands of images to train the system. While this is not a small number, this is far from being “big data.” In the next section we describe how to scale this process to cluster size processing, making this virtually limitless for the number of images we would be capable of analyzing.</span>
-   <span class="c11 c25">Test the model with a different OSM feature</span><span class="c11">: We have tried one particular feature but, as usual, we only learn how to generalize a method when we have tried a set of them. Applying this methodology to other OSM features would likely improve the overall fitting.</span>
-   <span class="c11 c25">Correcting the bounding box orientation</span><span class="c11">: In the images, it’s rare that all the tennis courts are aligned in the same way, using the bounding box to rotate all features to have the same alignment would help algorithms where this is important (unlike </span><span>local feature detector described below).</span>
-   <span class="c25">Better features</span><span>: We are using the bounding box to define the object we want to identify. However, but for more complex elements we might want to be more precise than that. This might require manual editing of every training image, but the better the training set, the better the results.</span>

<!-- -->

-   <span class="c25">Other algorithms</span><span>: We have used </span><span class="c20">opencv\_traincascade</span><span>, that supports both Haar and LBP (Local Binary Patterns) features but these are not the only ones. Two specific detectors that could be of use in this case are SIFT</span><sup>[\[8\]](#ftnt8)</sup><span>, and SURF</span><sup>[\[9\]](#ftnt9)</sup><span>, a local feature detector. These detectors improve extraction from the training image even under changes in image scale, noise and illumination, which is likely to happen in satellite imagery.</span>

<span></span>

<span>Setting up a cluster computing system with Apache Spark</span>
====================================================================

<span></span>

<span>In the previous section, we mentioned that one obvious improvement to our machine learning flow is to substantially increase the number of images we have used for training purposes, or as Herman Narula</span><sup>[\[10\]](#ftnt10)</sup><span> says: “</span><span class="c25">the cool stuff only happens at scale</span><span>”. In order to do this, we need a tool like Apache Spark to handle the extra load. Just relying on a more powerful machine VM won’t be enough for practical reasons.</span>

<span></span>

<span>In the following pages we show how to deploy a Spark Cluster in Amazon’s cloud, and how to run a simple mapreduce job. This is a cost efficient way of running Spark and a popular solution among startups. Other possibilities include platforms as service (PaaS) like Databricks</span><sup>[\[11\]](#ftnt11)</sup><span> (founded by the creators of Spark), or IBM Bluemix</span><sup>[\[12\]](#ftnt12)</sup><span>. This last approach is not covered in this document.</span>

<span></span>

<span>Apache Spark is a fast and general cluster computing system for big data that brings considerable performance improvements over existing tools. It was developed by the AMPLab</span><sup>[\[13\]](#ftnt13)</sup><span> at UC Berkeley and, unlike Hadoop</span><sup>[\[14\]](#ftnt14)</sup><span>, “</span><span class="c25">Spark's in-memory primitives provide performance up to 100 times faster for certain applications. By allowing user programs to load data into a cluster's memory and query it repeatedly, Spark is well suited to machine learning algorithms.</span><span>”</span>

<span></span>

<span>Technically, from the official documentation:</span>

<span></span>

<span>“Spark is </span><span class="c25">a fast and general-purpose cluster computing system. It provides high-level APIs in Java, Scala and Python, and an optimized engine that supports general execution graphs. It also supports a rich set of higher-level tools including Spark SQL for SQL and structured data processing, MLlib for machine learning, GraphX for graph processing, and Spark Streaming.</span><span>”</span>

<span></span>

<span>According to Spark inventor and MIT professor, Matei Zaharia, Spark is one of the most active and fastest growing open source big data cluster computing projects</span><sup>[\[15\]](#ftnt15)</sup><span>. Spark is supported by both Amazon’s and Google’s cloud, and it starting to have strong industry support</span><sup>[\[16\]](#ftnt16)</sup><span>.</span>

<span></span>

<span>Setting up Apache Spark</span>
------------------------------------

<span></span>

<span>We can install Spark on our laptop (or desktop computer) downloading one of the binaries available on the download page</span><sup>[\[17\]](#ftnt17)</sup><span>, Spark runs on both Windows and UNIX-like systems (e.g. Linux, Mac OS). The only requirement is to have an installation of Java</span><sup>[\[18\]](#ftnt18)</sup><span> 6+ on your computer (Spark is written in Scala and runs on the Java Virtual Machine). Also, we need a Python</span><sup>[\[19\]](#ftnt19)</sup><span> 2.7+ interpreter in order to run the scripts we will show in the following sections.</span>

<span></span>

<span>Follow these steps:</span>

1.  <span>Head to the downloads page.</span>
2.  <span>In “Choose a Spark release” choose the latest version available.</span>
3.  <span>In “Choose a package type” choose a “pre-built for Hadoop” version.</span>
4.  <span>Leave “Choose a download type” on its default value.</span>
5.  <span>Click on the “Download Spark” link and download the actual file.</span>

<span></span>

<span>Once you’ve downloaded the package, simply unpack it:</span>

<span></span>

<span class="c20">$ cd /your/target/folder</span>

<span class="c20">$ tar zxf spark-1.3.1-bin-hadoop2.4.tgz</span>

<span class="c20">$ cd spark-1.3.1-bin-hadoop2.4</span>

<span></span>

<span>You can verify that Spark is installed correctly running a sample application</span><sup>[\[20\]](#ftnt20)</sup><span>:</span>

<span></span>

<span class="c20">$ ./bin/spark-submit examples/src/main/python/pi.py 10</span>

<span></span>

<span>You will see a long list of logging statements, and an output like the following:</span>

<span></span>

<span class="c20">Pi is roughly 3.142360</span>

<span></span>

<span>Although, as we can see, Spark can be run on someone’s laptop (or desktop computer, which is useful to prototype or quickly explore a dataset), its full potential comes when it’s run as part of a distributed cluster. Let’s see now a couple of ways we can use to run Spark on Amazon AWS (for real-world data analysis).</span>

<span></span>

<span>Running Spark on AWS Elastic Compute Cloud (EC2)</span>
-------------------------------------------------------------

<span></span>

<span>The official Spark distribution includes a script</span><sup>[\[21\]](#ftnt21)</sup><span> that simplifies the setup of Spark Clusters on EC2. This script uses Boto</span><sup>[\[22\]](#ftnt22)</sup><span> behind the scenes so you might want to set up your </span><span class="c20">boto.cfg</span><span> file so that you don’t have to type your </span><span class="c20">aws\_access\_key\_id</span><span> and </span><span class="c20">aws\_secret\_access\_key</span><span> every time.</span>

<span></span>

<span>Let’s assume that we have created a new keypair (</span><span class="c20">ec2-keypair</span><span>) with the AWS Console, and that we have saved it in a file (</span><span class="c20">ec2-keypair.pem</span><span>) with the right permissions (</span><span class="c20">chmod 600</span><span>). We are now going to create a 10 machines cluster called </span><span class="c20">worldbank-cluster</span><span> (</span><span class="c25">please note that this will incur in some costs</span><span>):</span>

<span></span>

<span class="c20">$ ./ec2/spark-ec2 \\</span>

<span class="c20">    --key-pair=ec2-keypair \\</span>

<span class="c20">    --identity-file=ec2-keypair.pem \\</span>

<span class="c20">    --slaves=10 \\</span>

<span class="c20">    launch worldbank-cluster</span>

<span></span>

<span>Once the cluster is created (it will take a few minutes), we can login (via SSH) to our brand new cluster with the following command:</span>

<span></span>

<span class="c20">$ ./ec2/spark-ec2 \\</span>

<span class="c20">    --key-pair=ec2-keypair \\</span>

<span class="c20">    --identity-file=ec2-keypair.pem \\</span>

<span class="c20">    login worldbank-cluster</span>

<span></span>

<span>And we can run the same example code (or any other Spark application) with:</span>

<span></span>

<span class="c20">$ cd spark</span>

<span class="c20">$ ./bin/spark-submit examples/src/main/python/pi.py 10</span>

<span></span>

<span>(Spark comes pre-installed</span><sup>[\[23\]](#ftnt23)</sup><span> on </span><span class="c20">/root/spark</span><span>.)</span>

<span></span>

<span>Remember to destroy the cluster once you’re done with it:</span>

<span></span>

<span class="c20">$ ./ec2/spark-ec2 \\</span>

<span class="c20">    --delete-groups \\</span>

<span class="c20">    destroy worldbank-cluster</span>

<span></span>

<span>You could also stop (</span><span class="c20">./ec2/spark-ec2 stop worldbank-cluster</span><span>) and start (</span><span class="c20">./ec2/spark-ec2 stop worldbank-cluster</span><span>) the cluster without having to destroy it.</span>

<span></span>

<span>Running Spark on AWS EMR (Elastic MapReduce)</span><sup>[\[24\]](#ftnt24)</sup>
-------------------------------------------------------------------------------------

<span></span>

<span>Because Spark is compatible with Apache Hadoop</span><sup>[\[25\]](#ftnt25)</sup><span> we can use EMR as our Spark cluster for data processing. We are going to use the AWS command line interface</span><sup>[\[26\]](#ftnt26)</sup><span> to manage this new EMR, cluster and we assume you have it installed.</span>

<span></span>

<span>Before creating the cluster, make sure that you have created the default roles (this is a one-time setup command):</span>

<span></span>

<span class="c20">$ aws emr create-default-roles</span>

<span></span>

<span>Then, you can create the cluster with this command (again called </span><span class="c20">worldbank-cluster</span><span> with 10 machines</span><span>).</span>

<span></span>

<span class="c20">$ aws emr create-cluster \\</span>

<span class="c20">    --name worldbank-cluster \\</span>

<span class="c20">    --ami-version 3.7.0 \\</span>

<span class="c20">    --instance-type m3.xlarge \\</span>

<span class="c20">    --instance-count 10 \\</span>

<span class="c20">    --ec2-attributes KeyName=ec2-keypair \\</span>

<span class="c20">    --applications Name=Hive \\</span>

<span class="c20">    --use-default-roles \\</span>

<span class="c20">    --bootstrap-actions \\</span>

<span class="c20">      Path=s3://support.elasticmapreduce/spark/install-spark</span>

<span></span>

<span>Make sure you take note of the cluster ID (for example, </span><span class="c20">j-1A2BCD34EFG5H</span><span>). Again, take into account this could incur in Amazon AWS costs.</span>

<span></span>

<span>If you are already familiar with AWS and AWS EMR, you will notice that this is a pretty standard setup. The big difference is in the last line, that includes the S3 location for the Spark installation bootstrap action.</span>

<span></span>

<span>You can then perform the usual tasks on EMR clusters, like describe:</span>

<span></span>

<span class="c20">$ aws emr describe-cluster \\</span>

<span class="c20">    --cluster-id j-1A2BCD34EFG5H</span>

<span></span>

<span>or list instances:</span>

<span></span>

<span class="c20">$ aws emr list-instances \\</span>

<span class="c20">    --cluster-id j-1A2BCD34EFG5H</span>

<span></span>

<span>Once the EMR cluster has been created (it will take a few minutes), you can login via SSH, like we did in the previous section:</span>

<span></span>

<span class="c20">$ aws emr ssh \\</span>

<span class="c20">    --cluster-id j-1A2BCD34EFG5H \\</span>

<span class="c20">    --key-pair-file ec2-keypair.pem</span>

<span></span>

<span>And execute your Spark application with:</span>

<span></span>

<span class="c20">$ cd spark</span>

<span class="c20">$ ./bin/spark-submit examples/src/main/python/pi.py 10</span>

<span></span>

<span>(Spark comes pre-installed on </span><span class="c20">/home/hadoop</span><span>.)</span>

<span></span>

<span>Finally, you can terminate the cluster with:</span>

<span></span>

<span class="c20">$ aws emr terminate-clusters \\</span>

<span class="c20">    --cluster-id j-1A2BCD34EFG5H</span>

<span></span>

<span>Machine Learning on Google’s Cloud</span>
===============================================

<span></span>

<span>During the time of this assignment, Google held its annual developer conference, Google I/O 2015, where </span><span class="c15">[machine learning related topics](https://www.google.com/url?q=http://techcrunch.com/2015/05/31/io-spotlights-googles-machine-learning-smarts/?ncid%3Drss%23.1j7bir:c0bG&sa=D&usg=AFQjCNGk_DlCQ7MKWYhZC8nydEHTMyRAMg)</span><span> were at the core of the new products and development</span><span>. This section summarizes the current status of tools on Google’s Cloud to support machine learning processes and some of the announcements made during the conference.</span>

<span></span>

<span>New developments</span>
-----------------------------

<span></span>

<span>During the conference keynote, machine learning was mentioned directly (“</span><span class="c25">machine learning</span><span>”) or indirectly (“</span><span class="c25">computer vision</span><span>”, “</span><span class="c25">natural language processing</span><span>”, “</span><span class="c25">deep neural networks</span><span>”) about a dozen times. This can be visualized in the following word cloud that we have built</span><sup>[\[27\]](#ftnt27)</sup><span> where the terms “machine” and “learning” are highlighted:</span>

<span style="overflow: hidden; display: inline-block; margin: 0.00px 0.00px; border: 0.00px solid #000000; transform: rotate(0.00rad) translateZ(0px); -webkit-transform: rotate(0.00rad) translateZ(0px); width: 624.00px; height: 286.67px;">![Wordle-IO2015-highlights.png](readme_images/image04.png)</span>

<span></span>

<span>Products</span>
---------------------

<span></span>

<span>The two main products benefitting from recent machine learning developments at Google, as stated during the keynote, are:</span>

1.  <span>Google Photos</span><sup>[\[28\]](#ftnt28)</sup><span>. This new service is now available, and its search input is the main point of access for computer vision and machine learning functionality. Users can search by person, or image content, for example.</span>
2.  <span>Google Now and Google Now on Tap</span><sup>[\[29\]](#ftnt29)</sup><span>. This new product will be present in the future version of Android M, still unpublished.</span>

<span></span>

<span style="overflow: hidden; display: inline-block; margin: 0.00px 0.00px; border: 0.00px solid #000000; transform: rotate(0.00rad) translateZ(0px); -webkit-transform: rotate(0.00rad) translateZ(0px); width: 624.00px; height: 326.67px;">![Now\_I-O-v10.4TW.png](readme_images/image09.png)</span>

<span class="c13">Source: Google</span>

<span></span>

<span>Technologies</span>
-------------------------

<span></span>

<span>Unfortunately, Google is not releasing much information about the actual technologies they are using in their machine learning efforts. The exception might be deep neural networks. This is a quote from Sundar Pichai, Senior Vice President at Google for Android, Chrome, and Google Apps, during the keynote:</span>

<span></span>

<span class="c25">“You know, in this query, what looked like a simple query, we understood voice, we did natural language processing, we are doing image recognition, and, finally, translation, and making it all work in an instant. The reason we are able to do all of this is thanks to the investments we have made in machine learning. Machine learning is what helps us answer the question, what does a tree frog look like, from millions of images around the world. You know, the computers can go through a lot of data and understand patterns. It turns out the tree frog is actually the third picture there. The reason we are able to do that so much better in the last few years is thanks to an advance in the technology called deep neural nets. Deep neural nets are a hierarchical, layered learning system. So we learn in layers. The first layer can understand lines and edges and shadows and shapes. A second layer may understand things like like ears, legs, hands, and so on. And the final layer understands the entire image. We have the best investment in machine learning over the past many years, and we believe we have the best capability in the world. Our current deep neural nets are over 30 layers deep. It is what helps us when you speak to Google, our word error rate has dropped from a 23% to 8% in just over a year and that progress is due to our investment in machine learning.”</span>

<span></span>

<span>Artificial neural networks are a well known architecture in deep learning</span><sup>[\[30\]](#ftnt30)</sup><span>.</span>

<span></span>

<span style="overflow: hidden; display: inline-block; margin: 0.00px 0.00px; border: 0.00px solid #000000; transform: rotate(0.00rad) translateZ(0px); -webkit-transform: rotate(0.00rad) translateZ(0px); width: 624.00px; height: 458.67px;">![15 - 1.jpg](readme_images/image08.jpg)</span>

<span class="c13">Deep neural networks during Google I/O 2015 keynote</span><sup>[\[31\]](#ftnt31)</sup>

<span></span>

<span>Lack of new developer options</span>
------------------------------------------

<span></span>

<span>Unfortunately, the new products announced by Google are not immediately accompanied by new developer tools that we could benefit from to create advanced machine learning processing in an easier way, leveraging Google’s infrastructure.</span>

<span></span>

<span>We had conversations with Google engineers and Google Developer Experts and these are a few items we learned:</span>

-   <span>No immediate announcements regarding new machine learning tools, related or not to the new Google Now on Tap product.</span>
-   <span>No immediate announcements regarding new computer vision tools related to the new Google Photos product.</span>
-   <span>The Prediction API remains the recommended tool for machine learning in the cloud with a 99.9% availability service level agreement.</span>
-   <span>The Prediction API is better suited for numeric or text input that can output hundreds of discrete categories or continuous values. It is unclear the algorithms used by Google in order to generate the predictions.</span>
-   <span>Computer Vision analysis requires custom tools on top of Google Compute Engine (the equivalent of Amazon’s EC2). Preemptible VMs (instances that might be terminated, or preempted, at any moment) remain the best option for affordable computing and are a common solution.</span>
-   <span>Geographic analysis requires custom tools on top of Google Compute Engine as Cloud SQL has no support for PostgreSQL (and therefore, PostGIS). The Google Maps API for Work product is better suited for visualization than analysys. Internally, Google seems to solve this problem with Spanner</span><sup>[\[32\]](#ftnt32)</sup><span>.</span>
-   <span>An alternative to GCE is the Container Engine, that allows to run Docker containers on Google Cloud Platform, powered by Kubernetes</span><sup>[\[33\]](#ftnt33)</sup><span>. Google Container Engine schedules containers, based on declared needs, on a managed cluster of virtual machines.</span>

<span></span>

<span>Current tools</span>
--------------------------

<span></span>

<span>Finally, and in order to be comprehensive, these are the current tools that Google provides for machine learning and big data as part of their cloud offering:</span>

-   <span>BigQuery: Analyzes Big Data in the cloud, it runs fast, SQL-like queries against multi-terabyte datasets in seconds. Gives real-time insights about data.</span>
-   <span>Dataflow (</span><span class="c25">beta</span><span>): Builds, deploys, and runs data processing pipelines that scales to solve key business challenges. It enables reliable execution for large-scale data processing scenarios such as ETL, analytics, real-time computation, and process orchestration.</span>
-   <span>Pub/Sub (</span><span class="c25">beta</span><span>): Connects services with reliable, many-to-many, asynchronous messaging hosted on Google's infrastructure. Cloud Pub/Sub automatically scales as needed and provides a foundation for building global services.</span>
-   <span>Prediction API: Uses Google’s machine learning algorithms to analyze data and predict future outcomes using a RESTful interface.</span>

<span></span>

### <span>Discount code</span>

<span></span>

<span>If there’s any interest in trying any of these technologies, we can provide a $500 discount code that was shared with attendees. To redeem it, please follow the following instructions (this offer must be claimed by </span><span class="c25">June 15th</span><span>):</span>

1.  <span>Go to </span><span class="c15">[http://g.co/CloudStarterCredit](https://www.google.com/url?q=http://g.co/CloudStarterCredit&sa=D&usg=AFQjCNHV7f68FPlu6ivUgok5wpalZ5GlLA)</span><span> </span>
2.  <span>Click Apply Now</span>
3.  <span>Complete the form with code: </span><span class="c47">GCP15</span>

<span></span>

<span>Reference Materials</span>
================================

<span></span>

<span>Finally, we present a few references that can help the reader deepen their knowledge of all the areas mentioned in this report.</span>

<span>Code</span>
-----------------

<span></span>

<span>We have set a GitHub repository</span><sup>[\[34\]](#ftnt34)</sup><span> for the code of this project:</span>

-   <span>Machine Learning for Dev: </span><span class="c15">[https://github.com/zugaldia/ml4dev](https://www.google.com/url?q=https://github.com/zugaldia/ml4dev&sa=D&usg=AFQjCNErj_8y8tyVdStsBD3Jun7quMAijQ)</span><span> </span>

<span></span>

<span>Books</span>
------------------

<span></span>

<span>These are a few good books that expand on the tools and methodologies that we’ve used throughout this document:</span>

-   <span class="c15">[Data Science from Scratch: First Principles with Python](https://www.google.com/url?q=http://shop.oreilly.com/product/0636920033400.do&sa=D&usg=AFQjCNENjJbXwVvzp9Sqk-6NPIjwh48WIg)</span><span>, by Joel Grus. Publisher: O'Reilly Media (release Date: April 2015).</span>
-   <span class="c15">[Learning Spark: Lightning-Fast Big Data Analysis](https://www.google.com/url?q=http://shop.oreilly.com/product/0636920028512.do&sa=D&usg=AFQjCNGs5b-zdPdgC0N9wet5JKOmD5CQOg)</span><span>, by Holden Karau, Andy Konwinski, Patrick Wendell, Matei Zaharia. Publisher: O'Reilly Media (release Date: January 2015).</span>
-   <span class="c15">[Advanced Analytics with Spark: Patterns for Learning from Data at Scale](https://www.google.com/url?q=http://shop.oreilly.com/product/0636920035091.do&sa=D&usg=AFQjCNGlWxc1KMa_BjQCJxGbQHfPtacwwg)</span><span>, by Sandy Ryza, Uri Laserson, Sean Owen, Josh Wills. Publisher: O'Reilly Media (release Date: April 2015).</span>

<span></span>

<span>Websites</span>
---------------------

-   <span class="c15">[Apache Spark](https://www.google.com/url?q=https://spark.apache.org/&sa=D&usg=AFQjCNG9LgiHTP_hHJlTAXB47N4q-Qt2JQ)</span><span>: Fast and general engine for large-scale data processing.</span>
-   <span class="c15">[Mahotas](https://www.google.com/url?q=http://mahotas.readthedocs.org&sa=D&usg=AFQjCNGo5xI_v4uQvHWhBAe7O7xONdY1nA)</span><span>: Computer Vision in Python.</span>
-   <span class="c15">[OpenCV](https://www.google.com/url?q=http://www.opencv.org&sa=D&usg=AFQjCNGYk_Njg5BHJmfZ6hC25FKoieSp-g)</span><span> (Open Source Computer Vision Library): An open source computer vision and machine learning software library.</span>
-   <span class="c15">[scikit-learn](https://www.google.com/url?q=http://scikit-learn.org&sa=D&usg=AFQjCNH2dhhb4jUPTAd-U-W3EOulW_AWEw)</span><span>: Machine Learning in Python.</span>

<span></span>

------------------------------------------------------------------------

[\[1\]](#ftnt_ref1)<span class="c13"> </span><span class="c10">[https://en.wikipedia.org/wiki/Machine\_learning](https://www.google.com/url?q=https://en.wikipedia.org/wiki/Machine_learning&sa=D&usg=AFQjCNGyHrOE0j7i4QL3JdG19NXl_90r3A)</span><span class="c13"> </span>

[\[2\]](#ftnt_ref2)<span class="c13"> </span><span class="c10">[http://www.opencv.org](https://www.google.com/url?q=http://www.opencv.org&sa=D&usg=AFQjCNGYk_Njg5BHJmfZ6hC25FKoieSp-g)</span><span class="c13"> </span>

[\[3\]](#ftnt_ref3)<span class="c13"> This process is described in detail here: </span><span class="c10">[http://docs.opencv.org/doc/user\_guide/ug\_traincascade.html](https://www.google.com/url?q=http://docs.opencv.org/doc/user_guide/ug_traincascade.html&sa=D&usg=AFQjCNG3Eb-gzh-2tq1R9sp1VZOSSeqD-Q)</span><span class="c13"> </span>

[\[4\]](#ftnt_ref4)<span class="c13"> </span><span class="c10">[https://www.mapbox.com/commercial-satellite/](https://www.google.com/url?q=https://www.mapbox.com/commercial-satellite/&sa=D&usg=AFQjCNGFCHNLJBqqFl8-wIe83acCV3_TjA)</span><span class="c13"> </span>

[\[5\]](#ftnt_ref5)<span class="c13"> </span><span class="c10">[http://wiki.openstreetmap.org/wiki/Overpass\_API](https://www.google.com/url?q=http://wiki.openstreetmap.org/wiki/Overpass_API&sa=D&usg=AFQjCNFizwee0VtdA_2nr6BTWMeO_XqveA)</span><span class="c13"> </span>

[\[6\]](#ftnt_ref6)<span class="c13"> </span><span class="c10">[https://www.flickr.com/places/info/24875662](https://www.google.com/url?q=https://www.flickr.com/places/info/24875662&sa=D&usg=AFQjCNHrFDwaXx9x2QzG0zseDrj0dwRMJQ)</span><span class="c13"> </span>

[\[7\]](#ftnt_ref7)<span class="c13"> OpenCV detectMultiScale() minNeighbors parameter: </span><span class="c10">[http://stackoverflow.com/questions/22249579/opencv-detectmultiscale-minneighbors-parameter](https://www.google.com/url?q=http://stackoverflow.com/questions/22249579/opencv-detectmultiscale-minneighbors-parameter&sa=D&usg=AFQjCNG4ACJg-odMBGSN8T_yTZ3wRr-ZBw)</span><span class="c13"> </span>

[\[8\]](#ftnt_ref8)<span class="c13"> </span><span class="c10">[http://opencv-python-tutroals.readthedocs.org/en/latest/py\_tutorials/py\_feature2d/py\_sift\_intro/py\_sift\_intro.html](https://www.google.com/url?q=http://opencv-python-tutroals.readthedocs.org/en/latest/py_tutorials/py_feature2d/py_sift_intro/py_sift_intro.html&sa=D&usg=AFQjCNHryI2TAtd3R0mwjLZgWijmRcFwSw)</span><span class="c13"> </span>

[\[9\]](#ftnt_ref9)<span class="c13"> </span><span class="c10">[http://opencv-python-tutroals.readthedocs.org/en/latest/py\_tutorials/py\_feature2d/py\_surf\_intro/py\_surf\_intro.html](https://www.google.com/url?q=http://opencv-python-tutroals.readthedocs.org/en/latest/py_tutorials/py_feature2d/py_surf_intro/py_surf_intro.html&sa=D&usg=AFQjCNHEZg-KgtHV9br4m7XxRXwYtKn0DA)</span><span class="c13"> </span>

[\[11\]](#ftnt_ref11)<span class="c13"> </span><span class="c10">[https://databricks.com/](https://www.google.com/url?q=https://databricks.com/&sa=D&usg=AFQjCNH0J9dnhfqQ9UFBME7LxhKHBExp4A)</span><span class="c13"> </span>

[\[12\]](#ftnt_ref12)<span class="c13"> </span><span class="c10">[https://developer.ibm.com/bluemix/](https://www.google.com/url?q=https://developer.ibm.com/bluemix/&sa=D&usg=AFQjCNG4uwjhYhxDIt03MqNb12wW72TxEQ)</span><span class="c13"> </span>

[\[13\]](#ftnt_ref13)<span class="c13">Algorithms, Machines, and People Lab: </span><span class="c10">[https://amplab.cs.berkeley.edu](https://www.google.com/url?q=https://amplab.cs.berkeley.edu&sa=D&usg=AFQjCNHaV5sMRCGT2D6EL_TjHEC6_Z2wdA)</span><span class="c13"> </span>

[\[14\]](#ftnt_ref14)<span class="c13"> </span><span class="c10">[https://en.wikipedia.org/wiki/Apache\_Spark](https://www.google.com/url?q=https://en.wikipedia.org/wiki/Apache_Spark&sa=D&usg=AFQjCNGnQS88pnPs4s1kLPU2U2yEPrMRng)</span><span class="c13"> </span>

[\[15\]](#ftnt_ref15)<span class="c13"> “</span><span class="c25 c13">Andreessen Horowitz Podcast: A Conversation with the Inventor of Spark</span><span class="c13">”: </span><span class="c10">[http://a16z.com/2015/06/24/a16z-podcast-a-conversation-with-the-inventor-of-spark/](https://www.google.com/url?q=http://a16z.com/2015/06/24/a16z-podcast-a-conversation-with-the-inventor-of-spark/&sa=D&usg=AFQjCNH1TEIJ0nFleR2v1rA0uKbAX3umZQ)</span><span class="c13"> </span>

[\[16\]](#ftnt_ref16)<span class="c13"> “</span><span class="c25 c13">IBM Pours Researchers And Resources Into Apache Spark Project</span><span class="c13">”: </span><span class="c10">[http://techcrunch.com/2015/06/15/ibm-pours-researchers-and-resources-into-apache-spark-project/](https://www.google.com/url?q=http://techcrunch.com/2015/06/15/ibm-pours-researchers-and-resources-into-apache-spark-project/&sa=D&usg=AFQjCNHFFm6S1kbJf8kiWt4EpT4GJOIn7w)</span><span class="c13"> </span>

[\[17\]](#ftnt_ref17)<span class="c13"> </span><span class="c10">[https://spark.apache.org/downloads.html](https://www.google.com/url?q=https://spark.apache.org/downloads.html&sa=D&usg=AFQjCNF223tQufgI-bWJK-L9XL1y_YYetw)</span><span class="c13"> </span>

[\[18\]](#ftnt_ref18)<span class="c13"> </span><span class="c10">[https://java.com/en/download/](https://www.google.com/url?q=https://java.com/en/download/&sa=D&usg=AFQjCNFODbfMl1s6o1TMuWM5O6KxFdlMpg)</span><span class="c13"> </span>

[\[19\]](#ftnt_ref19)<span class="c13"> </span><span class="c10">[https://www.python.org/downloads/](https://www.google.com/url?q=https://www.python.org/downloads/&sa=D&usg=AFQjCNEtGL1pmazbD2Cn8kP82nW08hA9mA)</span><span class="c13"> </span>

[\[20\]](#ftnt_ref20)<span class="c13"> </span><span class="c10">[https://github.com/apache/spark/blob/master/examples/src/main/python/pi.py](https://www.google.com/url?q=https://github.com/apache/spark/blob/master/examples/src/main/python/pi.py&sa=D&usg=AFQjCNHzshMJcsWnpLjRAm6jU0IUUSTXSA)</span><span class="c13"> </span>

[\[21\]](#ftnt_ref21)<span class="c13"> </span><span class="c10">[https://spark.apache.org/docs/latest/ec2-scripts.html](https://www.google.com/url?q=https://spark.apache.org/docs/latest/ec2-scripts.html&sa=D&usg=AFQjCNG4InBUVPt2CaH0cTVZ9cBWbKK4rQ)</span><span class="c13"> </span>

[\[22\]](#ftnt_ref22)<span class="c13"> </span><span class="c10">[http://aws.amazon.com/sdk-for-python/](https://www.google.com/url?q=http://aws.amazon.com/sdk-for-python/&sa=D&usg=AFQjCNHZ3SpFZOvZsKvEg5Aht_doQU-ZoQ)</span><span class="c13"> </span>

[\[23\]](#ftnt_ref23)<span class="c13">Together with </span><span class="c13 c20">ephemeral-hdfs</span><span class="c13">, </span><span class="c13 c20">hadoop-native</span><span class="c13">, </span><span class="c13 c20">mapreduce</span><span class="c13">, </span><span class="c13 c20">persistent-hdfs</span><span class="c13">, </span><span class="c13 c20">scala</span><span class="c13">, and </span><span class="c13 c20">tachyon</span><span class="c13">.</span>

[\[24\]](#ftnt_ref24)<span class="c13"> After this section was written, Amazon announced </span><span class="c10">[improved support for Apache Spark on EMR](https://www.google.com/url?q=http://aws.amazon.com/elasticmapreduce/details/spark/&sa=D&usg=AFQjCNFw_bLgw2IkTVfXFRi7mQHmgfoVbw)</span><span class="c13">. We can now create an Amazon EMR cluster with Apache Spark from the AWS Management Console, AWS CLI, or SDK by choosing AMI 3.8.0 and adding Spark as an application. Amazon EMR currently supports Spark version 1.3.1 and utilizes Hadoop YARN as the cluster manager. To submit applications to Spark on your Amazon EMR cluster, you can add Spark steps with the Step API or interact directly with the Spark API on your cluster's master node.</span>

[\[25\]](#ftnt_ref25)<span class="c13"> In fact, Spak can run in Hadoop clusters through YARN or Spark's standalone mode, and it can process data in HDFS, HBase, Cassandra, Hive, and any Hadoop InputFormat.</span>

[\[26\]](#ftnt_ref26)<span class="c13"> </span><span class="c10">[http://aws.amazon.com/cli/](https://www.google.com/url?q=http://aws.amazon.com/cli/&sa=D&usg=AFQjCNEeUjetXYx48qPOV4TianISyFKq9w)</span><span class="c13"> </span>

[\[28\]](#ftnt_ref28)<span class="c13"> </span><span class="c10">[http://photos.google.com](https://www.google.com/url?q=http://photos.google.com&sa=D&usg=AFQjCNGkD_cbBk3dhWoaqpil2R1BH5eOkw)</span><span class="c13"> </span>

[\[29\]](#ftnt_ref29)<span class="c13"> </span><span class="c10">[http://arstechnica.com/gadgets/2015/05/android-ms-google-now-on-tap-shows-contextual-info-at-the-press-of-a-button/](https://www.google.com/url?q=http://arstechnica.com/gadgets/2015/05/android-ms-google-now-on-tap-shows-contextual-info-at-the-press-of-a-button/&sa=D&usg=AFQjCNEK0mmqy6rJ-KH9d1JqRHiB5q1Epw)</span><span class="c13"> </span>

[\[30\]](#ftnt_ref30)<span class="c13"> </span><span class="c10">[http://en.wikipedia.org/wiki/Deep\_learning](https://www.google.com/url?q=http://en.wikipedia.org/wiki/Deep_learning&sa=D&usg=AFQjCNFqY_DelGkEKWYc6gPVRXAKT3Uw5g)</span><span class="c13"> </span>

[\[31\]](#ftnt_ref31)<span class="c13"> Photo courtesy of Allen Firstenberg, Google Developer Expert: </span><span class="c10">[https://plus.google.com/101852559274654726533/posts/Fp6Zz2fVmVz](https://www.google.com/url?q=https://plus.google.com/101852559274654726533/posts/Fp6Zz2fVmVz&sa=D&usg=AFQjCNFh9J-Ln8X3H6_xosUQ2gunOw4tnw)</span><span class="c13"> </span>

[\[32\]](#ftnt_ref32)<span class="c13"> </span><span class="c10">[http://research.google.com/archive/spanner.html](https://www.google.com/url?q=http://research.google.com/archive/spanner.html&sa=D&usg=AFQjCNG9zg0_bWzXXClX01JE7ft2Yn4QgQ)</span><span class="c13"> </span>

[\[33\]](#ftnt_ref33)<span class="c13"> </span><span class="c10">[http://kubernetes.io/](https://www.google.com/url?q=http://kubernetes.io/&sa=D&usg=AFQjCNEGMQWLu5IAyFXUxPInHteMwMETZA)</span><span class="c13"> </span>

[\[34\]](#ftnt_ref34)<span class="c13"> Contact Antonio Zugaldia &lt;</span><span class="c10"><antonio@zugaldia.net></span><span class="c13">&gt; if you need access.</span>

[\[f\]](#cmnt_ref6)<span class="c24">From Google I get "The Tennis Industry Association website indicates in their National Database Court Report that there are an estimated 270,000 courts in the USA" so it seems fairly good</span>

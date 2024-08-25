# Summary
The code processes images by extracting superpixels and keypoints, constructing graphs based on these features, and analyzing the graphs' network properties. It then uses these properties as input to various machine learning models to classify the images. The process involves image segmentation, graph creation, and training multiple classifiers (e.g., Decision Tree, Random Forest) to evaluate and compare their accuracy in predicting image categories. The results are stored and analyzed to identify the most effective model.

## Explanation

**1.Imports**

we import various libraries for image processing `(cv2, skimage)`, numerical operations `(numpy, math)`, graph analysis `(networkx)`, data handling `(pandas, csv)`, and machine learning `(sklearn)`.

**2.Superpixel and Keypoint Extraction**

`extract_superpixels(image)`: Converts the grayscale image to RGB and uses the SLIC algorithm to segment the image into superpixels, returning the segments and the number of superpixels.

`extract_keypoints(image)`: Uses OpenCV's SIFT algorithm to detect keypoints in the image, returning the keypoints and their count.

**3.Coordinate Calculation**

`calculate_coordinatesS(segments)`: Computes the centroids of the superpixels.

`calculate_coordinatesK(keypoints)`: Extracts coordinates of keypoints from the image.

**4.Graph Creation and Analysis**

`create_graph(nodesS, threshold, num)`: Constructs a graph where nodes are either superpixel centroids or keypoints, and edges are formed if the distance between nodes is below a certain threshold.

`extract_network_properties(graph)`: Calculates various network properties (degree centrality, closeness centrality, betweenness centrality, PageRank, average neighbor degree) for the graph.

**5.Processing Images**

The code processes each image in a specified folder:
1. Extracts superpixels and keypoints.
2. Creates graphs based on these features.
3. Extracts network properties from the graphs.
4. Appends these properties to attribute vectors for later use.


**6. Saving Attributes to CSV**

attribute_vector1 and attribute_vector2 (for superpixels and keypoints respectively) are saved to separate CSV files (attribute_vector1.csv and attribute_vector2.csv).

> ps. our case ended with 4 atteribute vectors.

**7. Machine Learning**

`machine_learning()`: Trains and evaluates multiple machine learning models on the extracted attributes:
1. Loads the attribute data from CSV.
2. Encodes the data, splits it into training and test sets.
3. Trains several classifiers (e.g., Decision Tree, Random Forest, K-Nearest Neighbor, etc.).
4. Evaluates each classifier's accuracy and prints the results.

> We done this part on kaggle.com


## Our Machine learning result

We ran the code on 100 images which took so long to finish.
after that we get 4 atteribute_vectors files and upload them on kaggle.
our results ended on this :

![image](https://github.com/user-attachments/assets/699385a4-e996-4e20-8293-2ae3f20935c2)

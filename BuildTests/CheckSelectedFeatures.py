import os, sys, glob

taskType = sys.argv[1]
validationType = sys.argv[2]
description = sys.argv[3]
fsAlgorithmPaths = glob.glob(sys.argv[4])
selectedFeaturesFilePaths = glob.glob(sys.argv[5])
algorithmScriptColumnName = sys.argv[6]

if len(fsAlgorithmPaths) == 0:
    print "[FAILED] No feature-selection algorithm scripts were found!"
    exit(1)

if len(selectedFeaturesFilePaths) == 0:
    print "[FAILED] No selected-features files were found!"
    exit(1)

def validateMeanFeatureRank(algorithmFeatureData, featureName, lowerThreshold, upperThreshold, idText):
    featureIndices = [float(x.index(featureName) + 1) for x in algorithmFeatureData]
    meanFeatureIndex = sum(featureIndices) / len(featureIndices)

    if meanFeatureIndex > lowerThreshold and meanFeatureIndex <= upperThreshold:
        print "[PASSED] The mean feature index for %s was %.1f. {%s}" % (featureName, meanFeatureIndex, idText)
        return True
    else:
        print "[FAILED] The mean feature index for %s was %.1f. Expected was between %.1f and %.1f. {%s}" % (featureName, meanFeatureIndex, lowerThreshold, upperThreshold, idText)
        return False

failedAlgorithms = set()

for selectedFeaturesFilePath in selectedFeaturesFilePaths:
    data = [line.rstrip().split("\t") for line in file(selectedFeaturesFilePath)]
    headerItems = data.pop(0)
    featuresIndex = headerItems.index("Features")
    algorithmScriptIndex = headerItems.index(algorithmScriptColumnName)

    uniqueAlgorithmScripts = list(set([row[algorithmScriptIndex] for row in data]))

    if len(uniqueAlgorithmScripts) == 0:
        print "[FAILED] No algorithm scripts could be found."
        exit(1)

    for algorithmScript in uniqueAlgorithmScripts:
        idText = "%s - %s - %s - %s" % (taskType, validationType, selectedFeaturesFilePath, algorithmScript)
        algorithmFeatureData = [row[featuresIndex].split(",") for row in data if row[algorithmScriptIndex] == algorithmScript]

        if description.startswith("StrongSignal"):
            lowerThreshold = 0
            upperThreshold = 20
        elif description.startswith("NoSignal"):
            lowerThreshold = 15
            upperThreshold = len(algorithmFeatureData[0])

        for i in range(1, 6):
            success = validateMeanFeatureRank(algorithmFeatureData, "Feature%s" % i, lowerThreshold, upperThreshold, idText)
            if not success:
                failedAlgorithms.add(algorithmScript)

        for i in range(51, 56):
            success = validateMeanFeatureRank(algorithmFeatureData, "Feature%s.Low" % i, lowerThreshold, upperThreshold, idText)
            if not success:
                failedAlgorithms.add(algorithmScript)
            success = validateMeanFeatureRank(algorithmFeatureData, "Feature%s.Medium" % i, lowerThreshold, upperThreshold, idText)
            if not success:
                failedAlgorithms.add(algorithmScript)

print "\n[TEST SUMMARY]\n"
if len(failedAlgorithms) > 0:
    print "The following algorithm(s) failed at least once:"
    for algorithm in failedAlgorithms:
        print "  %s" % algorithm
    exit(1)
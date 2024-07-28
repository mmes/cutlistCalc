import csv
import sys
import os

stockLength = float(sys.argv[1])
transLength = float(sys.argv[2])
csvFile = sys.argv[3]
useMaxLegths = sys.argv[4] == "true"

outDir = os.path.dirname(os.path.abspath(csvFile))
outFile = os.path.join(outDir,"cutlist.csv")

print("Generating cutlist from: " + csvFile);
print("Using stock length: " + str(stockLength));
print("Max transport length: " + str(transLength));

lengthColIndex = 0
foundLength = False
cutLengths = []

with open(csvFile, mode ='r')as file:
  csvData = csv.reader(file)

  for row in csvData:
        if not foundLength:
           try:
               lengthColIndex = row.index("length")
               foundLength = True
           except ValueError:
               print("Expected a row titled 'length'")
        else:
            cutLengths.append(float(row[lengthColIndex]))

needSplits = True

while needSplits:
    cutLengths.sort()
    needSplits = False

    while cutLengths[-1] > transLength:
            tooLong = cutLengths[-1]
            cutLengths.pop()

            if(useMaxLegths):
                cutLengths.append(transLength)
                cutLengths.append(tooLong - transLength)
                print("Splitting " + str(tooLong) + " into " + str(transLength) + " and " + str(tooLong - transLength))
                needSplits = True
                # break
            else:
                cutLengths.append(tooLong / 2)
                cutLengths.append(tooLong / 2)
                print("Lenth " + str(tooLong) + " is too long so I cut it in half")
                needSplits = True
                # break
      
cutLengths.sort(reverse = True)

stockId = 0
# partsCut = 0
outCuts = []
# outCuts.append(["part length", "stock ID", "offset"])

stock = stockLength
cutRow = {}
didCut = True
offcut = 0
total = 0
leftover = 0
stackup = 0

while didCut:
    didCut = False

    for idx, l in enumerate(cutLengths):
        if(l <= stock):
            cutRow["part length"] = l
            cutRow["stock ID"] = stockId
            cutRow["offset"] = stockLength - stock + l

            stackup += l
            
            if(stackup >= transLength):
                cutRow["transport cut"] = True
                stackup = 0
            else:
                cutRow["transport cut"] = False
            
            stock = stock - l
            total += l
            del cutLengths[idx]
            didCut = True
            break
    
    if(didCut):
        if len(cutLengths) == 0:
            leftover = stock
        else:
            outCuts.append(cutRow)
            cutRow = {}
    
    if(didCut == False and len(cutLengths) > 0):
        offcut += stock
        stock = stockLength
        didCut = True
        stockId += 1

print("Neede stock: " + str(stockId + 1))
print("Offcut waste: " + str(offcut))
print("Total Cut: " + str(total))
print("Leftover: " + str(leftover))
print("Output: " + str(outFile))


with open(outFile, 'w', newline='') as csvfile:
    rowNames = ["part length", "stock ID", "offset", "transport cut"]
    writer = csv.DictWriter(csvfile, fieldnames=rowNames)
    writer.writeheader()
    writer.writerows(outCuts)
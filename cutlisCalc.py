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

partIdColIndex = 0
lengthColIndex = 0
foundColumns = False
cutLengths = []

with open(csvFile, mode ='r')as file:
  csvData = csv.reader(file)

  for row in csvData:
        if not foundColumns:
           try:
               partIdColIndex = row.index("section")
               lengthColIndex = row.index("round up")
               foundColumns = True
           except ValueError:
               print("Expected a row titled 'section' and 'round up'")
        else:
            cutLengths.append((int(row[partIdColIndex]), float(row[lengthColIndex])))

needSplits = True

while needSplits:
    cutLengths.sort(key=lambda x: x[1])
    needSplits = False

    while cutLengths[-1][1] > transLength:
            pId = cutLengths[-1][0]
            tooLong = cutLengths[-1][1]
            cutLengths.pop()

            if(useMaxLegths):
                cutLengths.append((pId, transLength))
                cutLengths.append((pId, tooLong - transLength))
                print("Splitting part ID " + str(pId) + " with lengh " + str(tooLong) + " into " + str(transLength) + " and " + str(tooLong - transLength))
                needSplits = True
                break
            else:
                cutLengths.append((pId, tooLong / 2))
                cutLengths.append((pId, tooLong / 2))
                print("Lenth " + str(tooLong) + " is too long so I cut it in half")
                needSplits = True
                break
      
cutLengths.sort(reverse = True, key=lambda x: x[1])

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
partIndex = 0

while didCut:
    didCut = False

    for idx, p in enumerate(cutLengths):
        pId = p[0]
        l = p[1]

        if(l <= stock):
            cutRow["part ID"] = pId
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
            cutLengths.pop(idx)
            didCut = True
            break
    
    if(didCut):
        outCuts.append(cutRow)
        
        if len(cutLengths) == 0:
            leftover = stock
        else:
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

outCuts.sort(key=lambda x: x["part ID"])

with open(outFile, 'w', newline='') as csvfile:
    rowNames = ["part ID", "part length", "stock ID", "offset", "transport cut"]
    writer = csv.DictWriter(csvfile, fieldnames=rowNames)
    writer.writeheader()
    writer.writerows(outCuts)
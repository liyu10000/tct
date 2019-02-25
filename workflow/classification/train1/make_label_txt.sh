find /home/nvme0/liyu/xcp-batch6.3/CELLS-half/valid/ACTINO -type f > ACTINO.txt
sed -i 's/$/ 0/g' ACTINO.txt
echo "ACTINO"

find /home/nvme0/liyu/xcp-batch6.3/CELLS-half/valid/AGC_A -type f > AGC_A.txt
sed -i 's/$/ 1/g' AGC_A.txt
echo "AGC_A"

find /home/nvme0/liyu/xcp-batch6.3/CELLS-half/valid/AGC_B -type f > AGC_B.txt
sed -i 's/$/ 2/g' AGC_B.txt
echo "AGC_B"

find /home/nvme0/liyu/xcp-batch6.3/CELLS-half/valid/ASCUS -type f > ASCUS.txt
sed -i 's/$/ 3/g' ASCUS.txt
echo "ASCUS"

find /home/nvme0/liyu/xcp-batch6.3/CELLS-half/valid/CC -type f > CC.txt
sed -i 's/$/ 4/g' CC.txt
echo "CC"

find /home/nvme0/liyu/xcp-batch6.3/CELLS-half/valid/EC -type f > EC.txt
sed -i 's/$/ 5/g' EC.txt
echo "EC"

find /home/nvme0/liyu/xcp-batch6.3/CELLS-half/valid/FUNGI -type f > FUNGI.txt
sed -i 's/$/ 6/g' FUNGI.txt
echo "FUNGI"

find /home/nvme0/liyu/xcp-batch6.3/CELLS-half/valid/GEC -type f > GEC.txt
sed -i 's/$/ 7/g' GEC.txt
echo "GEC"

find /home/nvme0/liyu/xcp-batch6.3/CELLS-half/valid/HSIL_B -type f > HSIL_B.txt
sed -i 's/$/ 8/g' HSIL_B.txt
echo "HSIL_B"

find /home/nvme0/liyu/xcp-batch6.3/CELLS-half/valid/HSIL_M -type f > HSIL_M.txt
sed -i 's/$/ 9/g' HSIL_M.txt
echo "HSIL_M"

find /home/nvme0/liyu/xcp-batch6.3/CELLS-half/valid/HSIL_S -type f > HSIL_S.txt
sed -i 's/$/ 10/g' HSIL_S.txt
echo "HSIL_S"

find /home/nvme0/liyu/xcp-batch6.3/CELLS-half/valid/LSIL_E -type f > LSIL_E.txt
sed -i 's/$/ 11/g' LSIL_E.txt
echo "LSIL_E"

find /home/nvme0/liyu/xcp-batch6.3/CELLS-half/valid/LSIL_F -type f > LSIL_F.txt
sed -i 's/$/ 12/g' LSIL_F.txt
echo "LSIL_F"

find /home/nvme0/liyu/xcp-batch6.3/CELLS-half/valid/MC -type f > MC.txt
sed -i 's/$/ 13/g' MC.txt
echo "MC"

find /home/nvme0/liyu/xcp-batch6.3/CELLS-half/valid/PH -type f > PH.txt
sed -i 's/$/ 14/g' PH.txt
echo "PH"

find /home/nvme0/liyu/xcp-batch6.3/CELLS-half/valid/RC -type f > RC.txt
sed -i 's/$/ 15/g' RC.txt
echo "RC"

find /home/nvme0/liyu/xcp-batch6.3/CELLS-half/valid/SC -type f > SC.txt
sed -i 's/$/ 16/g' SC.txt
echo "SC"

find /home/nvme0/liyu/xcp-batch6.3/CELLS-half/valid/SCC_G -type f > SCC_G.txt
sed -i 's/$/ 17/g' SCC_G.txt
echo "SCC_G"

find /home/nvme0/liyu/xcp-batch6.3/CELLS-half/valid/SCC_R -type f > SCC_R.txt
sed -i 's/$/ 18/g' SCC_R.txt
echo "SCC_R"

find /home/nvme0/liyu/xcp-batch6.3/CELLS-half/valid/TRI -type f > TRI.txt
sed -i 's/$/ 19/g' TRI.txt
echo "TRI"

find /home/nvme0/liyu/xcp-batch6.3/CELLS-half/valid/VIRUS -type f > VIRUS.txt
sed -i 's/$/ 20/g' VIRUS.txt
echo "VIRUS"


echo "merge all txts"
cat *.txt >> valid.txt
mv valid.txt ../
rm *.txt
mv ../valid.txt ./
wc -l valid.txt

echo "shuffle lines"
shuf -o valid.txt valid.txt
shuf -o valid.txt valid.txt
shuf -o valid.txt valid.txt
shuf -o valid.txt valid.txt
shuf -o valid.txt valid.txt
wc -l valid.txt
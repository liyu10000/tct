find /home/hdd0/Develop/liyu/batch6.4-608-to-299/original-hls09-rotated/valid/ACTINO -type f > ACTINO.txt
sed -i 's/$/ 0/g' ACTINO.txt
echo "done"

find /home/hdd0/Develop/liyu/batch6.4-608-to-299/original-hls09-rotated/valid/AGC -type f > AGC.txt
sed -i 's/$/ 1/g' AGC.txt
echo "done"

find /home/hdd0/Develop/liyu/batch6.4-608-to-299/original-hls09-rotated/valid/ASCUS -type f > ASCUS.txt
sed -i 's/$/ 2/g' ASCUS.txt
echo "done"

find /home/hdd0/Develop/liyu/batch6.4-608-to-299/original-hls09-rotated/valid/CC -type f > CC.txt
sed -i 's/$/ 3/g' CC.txt
echo "done"

find /home/hdd0/Develop/liyu/batch6.4-608-to-299/original-hls09-rotated/valid/EC -type f > EC.txt
sed -i 's/$/ 4/g' EC.txt
echo "done"

find /home/hdd0/Develop/liyu/batch6.4-608-to-299/original-hls09-rotated/valid/FUNGI -type f > FUNGI.txt
sed -i 's/$/ 5/g' FUNGI.txt
echo "done"

find /home/hdd0/Develop/liyu/batch6.4-608-to-299/original-hls09-rotated/valid/HSIL-SCC_G -type f > HSIL-SCC_G.txt
sed -i 's/$/ 6/g' HSIL-SCC_G.txt
echo "done"

find /home/hdd0/Develop/liyu/batch6.4-608-to-299/original-hls09-rotated/valid/LSIL -type f > LSIL.txt
sed -i 's/$/ 7/g' LSIL.txt
echo "done"

find /home/hdd0/Develop/liyu/batch6.4-608-to-299/original-hls09-rotated/valid/NORMAL -type f > NORMAL.txt
sed -i 's/$/ 8/g' NORMAL.txt
echo "done"

find /home/hdd0/Develop/liyu/batch6.4-608-to-299/original-hls09-rotated/valid/PH -type f > PH.txt
sed -i 's/$/ 9/g' PH.txt
echo "done"

find /home/hdd0/Develop/liyu/batch6.4-608-to-299/original-hls09-rotated/valid/SCC_R -type f > SCC_R.txt
sed -i 's/$/ 10/g' SCC_R.txt
echo "done"

find /home/hdd0/Develop/liyu/batch6.4-608-to-299/original-hls09-rotated/valid/TRI -type f > TRI.txt
sed -i 's/$/ 11/g' TRI.txt
echo "done"

find /home/hdd0/Develop/liyu/batch6.4-608-to-299/original-hls09-rotated/valid/VIRUS -type f > VIRUS.txt
sed -i 's/$/ 12/g' VIRUS.txt
echo "done"

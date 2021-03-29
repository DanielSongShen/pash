# remove this line since it hangs timeout 2 -i brightness | cut -f2 -d "" "" > ~/.currentbrightness; cat\
# execute once
#sed -e '46106d' $1                                                               
# likely-longest-pipelines.txt is locally stored
# strip the number of pipe column
#cut -f1 -d " " --complement  likely-longest-pipelines.txt > $PASH_TOP/evaluation/scripts/input/generated.file

## mp3 dataset ##
#apt-get install ffmpeg unrtf imagemagick
PW=$PWD/input #$PASH_TOP/evaluation/scripts/input/aliases
mkdir -p output
mkdir -p $PW
cd $PW
if [ ! -f tomhannen-20080409.tgz ]; then                                                 
    echo "Fetching Dataset"                                                   
    wget http://www.repository.voxforge1.org/downloads/SpeechCorpus/Trunk/Audio/Original/48kHz_16bit/tomhannen-20080409.tgz
    tar xf tomhannen-20080409.tgz
fi
rm -rf wav mp3
mkdir wav mp3 rtf
cd tomhannen-20080409/wav
# total 5.7 size of audio files
for i in *.wav; do
  FILE=$(basename "$i")
  for x in {1..20}; do cp $i "../../wav/$i$x.wav"; done
done
rm -rf ../../tomhannen-20080409
cd  $PW
wget https://jeroen.github.io/files/sample.rtf
for i in {0..10000}
do
    cp sample.rtf rtf/sample$i.rtf
done

if [ ! -f jpg1.tar.gz ]; then
    echo "Fetching Dataset"                                                   
    wget -O jpg1.tar.gz ftp://ftp.inrialpes.fr/pub/lear/douze/data/jpg1.tar.gz
    tar xf jpg1.tar.gz                                                            
fi                                                                            
mkdir -p tmp                                                                  
cd jpg/
for filename in *.jpg; do                                                     
    cp $filename ../tmp/${filename}_copy.jpg                                  
done
cd ../tmp
for filename in *.jpg; do                                                     
    cp $filename ../jpg/
done                                                                          
echo "JPGs copied"
rm -rf ../tmp
cd ..
rm -rf tmp
mkdir tmp
seq -w 1 100000 | xargs -P 100 -I{} sh -c 'num=$(echo {} | sed 's/^0*//');val=$(($num % 1000)); touch tmp/f{}.$val;'
echo "Generated 100000 empty files"

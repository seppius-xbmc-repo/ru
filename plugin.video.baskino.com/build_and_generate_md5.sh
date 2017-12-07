#!/usr/bin/env bash

#make version
regex="(plugin.*com)\S\sname.*version=\S(.*)\S\sprovider"
fileName=""
folderName=""
while read xml; do
    if [[ $xml =~ $regex ]]
    then
        echo "$xml matches regex: $regex"
        fileName=${BASH_REMATCH[1]}-${BASH_REMATCH[2]}.zip
        folderName=${BASH_REMATCH[1]}
        #print out capturing groups
        for (( i=0; i<${#BASH_REMATCH[@]}; i++))
        do
            echo -e "\tGroup[$i]: ${BASH_REMATCH[$i]}"
        done
    fi
done <addon.xml
echo ${fileName}
echo ${folderName}
cd ..
zip -FSr ${folderName}/${fileName} ${folderName} -x "*.zip" -x ".*" -x "*.md5" -x "*.sh" -x "*/.idea/*"
cd ${folderName}

#generate md5
for file in *.zip; do
md5sum "$file" > "${file/.zip/.zip.md5}";
git add "$file";
git add "${file/.zip/.zip.md5}"
done

cd ..
python2 ./addons_xml_generator.py
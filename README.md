# ciscoprime-statseeker
The script is designed to streamline network management processes by retrieving IP addresses from Cisco Prime, a network management platform, and subsequently deleting the associated Access Point (AP) names from Statseeker, an infrastructure monitoring and management tool. By integrating these two functionalities, the script enables network administrators to maintain an up-to-date and accurate inventory of network devices. It first collects the IP addresses of wireless access points from Cisco Prime. Then, it automatically identifies and removes the corresponding AP names from Statseeker's database, ensuring consistency and eliminating outdated or redundant information. 

# dependencies
# curlify

conda install -c conda-forge curlify

# Process XML elements

conda install -c conda-forge elementpath

conda install -c "conda-forge/label/cf201901" elementpath

conda install -c "conda-forge/label/cf202003" elementpath

conda install -c "conda-forge/label/gcc7" elementpath


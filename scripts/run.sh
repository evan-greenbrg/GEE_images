#!/bin/bash
river='TrinityTOA'
# poly="/Users/greenberg/Documents/PHD/Projects/Mobility/MethodsPaper/RiverData/BraidedRivers/Shapes/$river.gpkg"
poly="/Users/greenberg/Documents/PHD/Writing/MobilityMethods/Figures/PubFigures/Figure4_Meandering/Trinity/Trinity.gpkg"
dataset='landsatTOA'      # landsatSR, landsatTOA sentinel
start="01-01"   # Month-Day format with leading 0s
end="12-31"     # Month-Day format with leading 0s
start_year="2021"   
end_year="2021"     
out="/Users/greenberg/Documents/PHD/Writing/MobilityMethods/Figures/PubFigures/Figure4_Meandering/Trinity"

python ../GEE_images/main.py --poly $poly --dataset $dataset --start $start --end $end --start_year $start_year --end_year $end_year --out $out --river $river

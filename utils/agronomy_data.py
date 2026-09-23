"""
OptiCrop Agronomic Intelligence Knowledge Base.
Contains detailed agronomic dossiers for all 22 crops in the model,
plus the OptiBot AI reasoning engine with memory.
"""
import os

CROP_PROFILES = {
    'rice': {
        'display_name': 'Rice (Paddy)',
        'category': 'Cereal Grain',
        'season': 'Kharif (Monsoon)',
        'duration_days': '105 - 140 days',
        'water_need': 'Very High (150 - 250 cm)',
        'optimal_ph': '5.5 - 6.8',
        'ideal_temp': '20 - 35°C',
        'economic_yield': '3.8 - 6.2 tonnes / ha',
        'fertilizer_tips': 'Split Nitrogen application into 3 stages: 50% basal at transplanting, 25% at active tillering, and 25% at panicle emergence. Avoid excess N to prevent blast susceptibility.',
        'pest_control': 'Keep an eye for Stem Borer and Brown Planthopper. Maintain proper water drainage to manage fungal sheath blight.',
        'companion_crops': 'Azolla bio-fertilizer, Pigeonpeas on bunds, Blackgram/Lentil in post-harvest rotation.',
        'icon': 'bi-moisture',
        'accent_color': '#4A90E2'
    },
    'maize': {
        'display_name': 'Maize (Corn)',
        'category': 'Cereal Grain',
        'season': 'Kharif & Rabi',
        'duration_days': '90 - 115 days',
        'water_need': 'Moderate (50 - 75 cm)',
        'optimal_ph': '5.8 - 7.2',
        'ideal_temp': '18 - 27°C',
        'economic_yield': '4.5 - 7.5 tonnes / ha',
        'fertilizer_tips': 'Maize is a heavy feeder. Requires high Nitrogen. Apply Zinc Sulphate (25 kg/ha) at planting if soil shows micro-nutrient depletion.',
        'pest_control': 'Scout for Fall Armyworm early in the whorl stage. Apply neem oil or bio-pesticides at initial egg mass detection.',
        'companion_crops': 'Soybean, Cowpeas, Beans (three sisters polyculture).',
        'icon': 'bi-sun-fill',
        'accent_color': '#E5A93B'
    },
    'chickpea': {
        'display_name': 'Chickpea (Gram)',
        'category': 'Pulse / Legume',
        'season': 'Rabi (Winter)',
        'duration_days': '90 - 120 days',
        'water_need': 'Low (25 - 40 cm)',
        'optimal_ph': '6.0 - 8.0',
        'ideal_temp': '15 - 25°C',
        'economic_yield': '1.5 - 2.8 tonnes / ha',
        'fertilizer_tips': 'As a nitrogen-fixing legume, chickpea needs minimal N (20 kg/ha). Focus on Phosphorous (40-50 kg P2O5) to stimulate deep root nodulation.',
        'pest_control': 'Pod borer (Helicoverpa armigera) is common. Install pheromone traps (5/ha) and bird perches to control caterpillars.',
        'companion_crops': 'Mustard, Wheat, Safflower intercropping (6:1 row ratio).',
        'icon': 'bi-circle-half',
        'accent_color': '#C48A45'
    },
    'kidneybeans': {
        'display_name': 'Kidney Beans (Rajma)',
        'category': 'Pulse / Legume',
        'season': 'Rabi in Plains, Kharif in Hills',
        'duration_days': '100 - 130 days',
        'water_need': 'Moderate (45 - 60 cm)',
        'optimal_ph': '5.5 - 6.5',
        'ideal_temp': '15 - 24°C',
        'economic_yield': '1.8 - 2.5 tonnes / ha',
        'fertilizer_tips': 'Unlike other pulses, kidney beans have lower natural nodulation capacity. They benefit from moderate starter Nitrogen (60-80 kg/ha).',
        'pest_control': 'Watch out for Aphids and Anthracnose. Ensure well-drained loam soil to prevent root rot.',
        'companion_crops': 'Corn, Squash, Carrots.',
        'icon': 'bi-gem',
        'accent_color': '#8B263E'
    },
    'pigeonpeas': {
        'display_name': 'Pigeonpeas (Arhar / Red Gram)',
        'category': 'Pulse / Legume',
        'season': 'Kharif',
        'duration_days': '150 - 240 days',
        'water_need': 'Low to Moderate (60 - 80 cm)',
        'optimal_ph': '6.5 - 7.5',
        'ideal_temp': '22 - 32°C',
        'economic_yield': '1.4 - 2.2 tonnes / ha',
        'fertilizer_tips': 'Deep taproot system thrives in residual moisture. Apply 20 kg N and 50 kg P2O5 at sowing.',
        'pest_control': 'Protect during flowering against blister beetles and pod fly. Spray botanical neem formulations.',
        'companion_crops': 'Sorghum, Pearl Millet, Soybean.',
        'icon': 'bi-tree',
        'accent_color': '#A66B38'
    },
    'mothbeans': {
        'display_name': 'Moth Beans (Matki)',
        'category': 'Arid Legume',
        'season': 'Kharif',
        'duration_days': '75 - 90 days',
        'water_need': 'Extremely Low (20 - 35 cm)',
        'optimal_ph': '6.5 - 8.2',
        'ideal_temp': '25 - 38°C',
        'economic_yield': '0.8 - 1.4 tonnes / ha',
        'fertilizer_tips': 'Drought-hardy champion. Minimal fertilizer required; 10 kg N and 20 kg P per hectare is sufficient.',
        'pest_control': 'Highly resistant to most pests. Maintain weed-free conditions during the first 30 days.',
        'companion_crops': 'Bajra (Pearl Millet), Sesame.',
        'icon': 'bi-shield-fill-check',
        'accent_color': '#D29952'
    },
    'mungbean': {
        'display_name': 'Mung Bean (Green Gram)',
        'category': 'Pulse / Legume',
        'season': 'Kharif, Spring & Summer',
        'duration_days': '60 - 75 days (Ultra short cycle)',
        'water_need': 'Low (30 - 45 cm)',
        'optimal_ph': '6.2 - 7.5',
        'ideal_temp': '24 - 35°C',
        'economic_yield': '1.0 - 1.6 tonnes / ha',
        'fertilizer_tips': 'Inoculate seeds with Rhizobium and Phosphobacteria before sowing to boost yield by 15-20%.',
        'pest_control': 'Whitefly vector control is key to preventing Yellow Mosaic Virus (YMV).',
        'companion_crops': 'Sugar cane intercrop, Cotton intercrop.',
        'icon': 'bi-flower2',
        'accent_color': '#4E8752'
    },
    'blackgram': {
        'display_name': 'Blackgram (Urad Dal)',
        'category': 'Pulse / Legume',
        'season': 'Kharif & Rabi',
        'duration_days': '70 - 85 days',
        'water_need': 'Low (35 - 50 cm)',
        'optimal_ph': '6.0 - 7.5',
        'ideal_temp': '25 - 35°C',
        'economic_yield': '1.1 - 1.8 tonnes / ha',
        'fertilizer_tips': 'Apply DAP (Di-ammonium phosphate) at 50 kg/ha at sowing time for quick phosphorus availability.',
        'pest_control': 'Spray 2% DAP spray at flower initiation and 15 days later to prevent pod shedding.',
        'companion_crops': 'Paddy fallow, Maize, Sorghum.',
        'icon': 'bi-circle-fill',
        'accent_color': '#333333'
    },
    'lentil': {
        'display_name': 'Lentil (Masoor)',
        'category': 'Pulse / Legume',
        'season': 'Rabi (Winter)',
        'duration_days': '100 - 120 days',
        'water_need': 'Low (25 - 35 cm)',
        'optimal_ph': '6.0 - 7.8',
        'ideal_temp': '15 - 22°C',
        'economic_yield': '1.2 - 2.0 tonnes / ha',
        'fertilizer_tips': 'Apply Sulfur (20 kg/ha) along with Phosphorus to enhance protein content and seed weight.',
        'pest_control': 'Wilt and Rust can occur in waterlogged soils. Ensure raised beds in heavy soils.',
        'companion_crops': 'Barley, Mustard, Linseed.',
        'icon': 'bi-egg',
        'accent_color': '#C86843'
    },
    'pomegranate': {
        'display_name': 'Pomegranate',
        'category': 'Horticultural Fruit',
        'season': 'Perennial (Flowering in Mrig/Hasta/Ambe bahar)',
        'duration_days': 'Perennial (Fruits in 140-160 days from bloom)',
        'water_need': 'Moderate (Drip irrigation recommended)',
        'optimal_ph': '6.5 - 7.8',
        'ideal_temp': '22 - 38°C',
        'economic_yield': '12 - 18 tonnes / ha',
        'fertilizer_tips': 'Heavy Potassium feeder for fruit skin luster and aril sweetness. Apply farmyard manure (20kg/tree) in winter.',
        'pest_control': 'Bacterial blight (Telya) requires Bordeaux mixture (1%) prophylaxis during humid conditions.',
        'companion_crops': 'Short-duration pulses (Mung, Cowpea) during orchard establishment.',
        'icon': 'bi-heart-fill',
        'accent_color': '#C23B38'
    },
    'banana': {
        'display_name': 'Banana',
        'category': 'Fruit / Cash Crop',
        'season': 'Year-round planting',
        'duration_days': '11 - 14 months',
        'water_need': 'Very High (180 - 220 cm)',
        'optimal_ph': '6.0 - 7.5',
        'ideal_temp': '20 - 35°C',
        'economic_yield': '40 - 70 tonnes / ha',
        'fertilizer_tips': 'Highest Potassium consumer. Feed 200g N, 60g P, and 300g K per plant divided across growth stages.',
        'pest_control': 'Sigatoka leaf spot and Panama wilt. Use tissue-culture disease-free suckers and maintain good drainage.',
        'companion_crops': 'Turmeric, Ginger, Legumes in early months.',
        'icon': 'bi-lightning-charge-fill',
        'accent_color': '#F4B41A'
    },
    'mango': {
        'display_name': 'Mango (King of Fruits)',
        'category': 'Horticultural Orchard',
        'season': 'Perennial (Harvest April - July)',
        'duration_days': 'Perennial tree (Bloom to harvest: 100-120 days)',
        'water_need': 'Moderate (Drip irrigation during fruit sizing)',
        'optimal_ph': '5.5 - 7.5',
        'ideal_temp': '24 - 33°C',
        'economic_yield': '8 - 15 tonnes / ha',
        'fertilizer_tips': 'Apply paclobutrazol growth regulator for regular flowering. Supplement with Boron during panicle bloom.',
        'pest_control': 'Mango hoppers and powdery mildew during flowering. Timely sulfur dust prevents flower drop.',
        'companion_crops': 'Intercrop vegetables or legumes in the initial 4-5 years.',
        'icon': 'bi-trophy-fill',
        'accent_color': '#FF9F1C'
    },
    'grapes': {
        'display_name': 'Grapes (Vineyard)',
        'category': 'Horticultural Vine',
        'season': 'Perennial (Pruned in April & October)',
        'duration_days': '130 - 150 days from back-pruning',
        'water_need': 'Moderate (50 - 70 cm with precise drip scheduling)',
        'optimal_ph': '6.5 - 8.0',
        'ideal_temp': '15 - 35°C',
        'economic_yield': '20 - 30 tonnes / ha',
        'fertilizer_tips': 'Balanced NPK ratio with high potash for sugar brix accumulation. Foliar spray of Gibberellic Acid (GA3) for berry elongation.',
        'pest_control': 'Downy and Powdery mildew require strict weather-based preventive sprays.',
        'companion_crops': 'Cover crops like Clover or Rye grass between vine rows for weed suppression.',
        'icon': 'bi-collection-fill',
        'accent_color': '#6B2D5C'
    },
    'watermelon': {
        'display_name': 'Watermelon',
        'category': 'Cucurbit Fruit',
        'season': 'Zaid (Summer)',
        'duration_days': '80 - 100 days',
        'water_need': 'Moderate (40 - 60 cm, stop watering near harvest)',
        'optimal_ph': '6.0 - 7.0 (Sandy loam)',
        'ideal_temp': '24 - 32°C',
        'economic_yield': '25 - 45 tonnes / ha',
        'fertilizer_tips': 'Apply Potassium nitrate during fruit swelling for sweet red pulp. Cut off irrigation 7 days before harvest to concentrate sugars.',
        'pest_control': 'Protect young seedlings from red pumpkin beetle. Avoid overhead sprinkler to prevent fruit rot.',
        'companion_crops': 'Marigold (nematode control), Radish.',
        'icon': 'bi-water',
        'accent_color': '#E63946'
    },
    'muskmelon': {
        'display_name': 'Muskmelon (Cantaloupe)',
        'category': 'Cucurbit Fruit',
        'season': 'Zaid (Summer)',
        'duration_days': '75 - 90 days',
        'water_need': 'Moderate (35 - 50 cm)',
        'optimal_ph': '6.0 - 7.5',
        'ideal_temp': '25 - 34°C',
        'economic_yield': '15 - 25 tonnes / ha',
        'fertilizer_tips': 'Needs high Potassium and Calcium to prevent blossom end rot and achieve good netting on rind.',
        'pest_control': 'Fruit fly management with cue-lure traps (10 traps/ha).',
        'companion_crops': 'Corn (windbreak), Basil.',
        'icon': 'bi-sun',
        'accent_color': '#F77F00'
    },
    'apple': {
        'display_name': 'Apple Orchard',
        'category': 'Temperate Fruit',
        'season': 'High Altitude Perennial (Chill hours: 800 - 1200 hrs < 7°C)',
        'duration_days': 'Perennial (130 - 160 days from bloom)',
        'water_need': 'Moderate (75 - 100 cm annual rainfall / snowmelt)',
        'optimal_ph': '5.5 - 6.5 (Rich mountain loam)',
        'ideal_temp': '10 - 24°C',
        'economic_yield': '10 - 22 tonnes / ha',
        'fertilizer_tips': 'Apply Calcium chloride sprays to prevent bitter pit. Maintain high organic mulch around root zone.',
        'pest_control': 'Apple Scab requires captan/mancozeb sprays post petal-fall. Woolly aphid controlled with Aphelinus mali parasites.',
        'companion_crops': 'Daffodils, Chives, White clover under canopy.',
        'icon': 'bi-apple',
        'accent_color': '#D90429'
    },
    'orange': {
        'display_name': 'Orange (Citrus)',
        'category': 'Citrus Fruit',
        'season': 'Perennial (Harvest Nov - Feb)',
        'duration_days': 'Perennial (210 - 240 days from flowering)',
        'water_need': 'Moderate (90 - 120 cm with regulated deficit irrigation)',
        'optimal_ph': '6.0 - 7.5',
        'ideal_temp': '18 - 35°C',
        'economic_yield': '15 - 28 tonnes / ha',
        'fertilizer_tips': 'Citrus demands micronutrients: Zinc, Iron, Manganese, and Magnesium. Spray chelated micronutrient mixture twice yearly.',
        'pest_control': 'Citrus psylla (vector of Citrus Greening disease) and Leaf miner. Spray neem formulation on fresh flushes.',
        'companion_crops': 'Leguminous cover crops, Mustard.',
        'icon': 'bi-brightness-high-fill',
        'accent_color': '#FB8500'
    },
    'papaya': {
        'display_name': 'Papaya',
        'category': 'Tropical Fruit',
        'season': 'Year-round',
        'duration_days': '9 - 11 months to first harvest',
        'water_need': 'Moderate to High (Waterlogging strictly fatal)',
        'optimal_ph': '6.0 - 7.0',
        'ideal_temp': '22 - 35°C',
        'economic_yield': '60 - 90 tonnes / ha',
        'fertilizer_tips': 'Continuous feeder. Apply 200g each of N, P, and K per plant every 2 months under drip fertigation.',
        'pest_control': 'Papaya Ring Spot Virus (PRSV) spread by aphids. Plant border rows of maize and use reflective mulch.',
        'companion_crops': 'Ginger, Turmeric in first 4 months.',
        'icon': 'bi-flower3',
        'accent_color': '#FCBF49'
    },
    'coconut': {
        'display_name': 'Coconut Palm',
        'category': 'Plantation Cash Crop',
        'season': 'Perennial Coastal',
        'duration_days': 'Perennial (First nut harvest in 5-6 years, yields 60-80 yrs)',
        'water_need': 'High (130 - 230 cm rainfall or 40-50 L/palm/day)',
        'optimal_ph': '5.2 - 8.0 (Sandy/coastal alluvial)',
        'ideal_temp': '22 - 34°C',
        'economic_yield': '80 - 120 nuts / palm / year',
        'fertilizer_tips': 'High Potassium and Chlorine need (common salt: 1 kg NaCl/palm/yr promotes nut development). Apply 500g N, 320g P, 1200g K per adult palm.',
        'pest_control': 'Rhinoceros beetle and Red Palm Weevil. Use pheromone traps and neem seed kernel extract.',
        'companion_crops': 'Cocoa, Pepper, Nutmeg, Banana multi-tier agroforestry system.',
        'icon': 'bi-tree-fill',
        'accent_color': '#2A9D8F'
    },
    'cotton': {
        'display_name': 'Cotton (White Gold)',
        'category': 'Commercial Fiber',
        'season': 'Kharif',
        'duration_days': '150 - 180 days',
        'water_need': 'Moderate (50 - 75 cm)',
        'optimal_ph': '6.0 - 8.0 (Deep black cotton vertisol)',
        'ideal_temp': '21 - 32°C',
        'economic_yield': '2.0 - 3.5 tonnes seed cotton / ha',
        'fertilizer_tips': 'Avoid excessive vegetative Nitrogen growth. Apply Boron and Magnesium sulfate at square formation.',
        'pest_control': 'Pink Bollworm management using pheromone mating disruption and refuge non-Bt border rows.',
        'companion_crops': 'Pigeonpea (trap crop), Castor, Marigold.',
        'icon': 'bi-cloud-fill',
        'accent_color': '#457B9D'
    },
    'jute': {
        'display_name': 'Jute (Golden Fiber)',
        'category': 'Commercial Fiber',
        'season': 'Kharif / Pre-monsoon',
        'duration_days': '120 - 135 days',
        'water_need': 'High (150 - 200 cm, high humidity > 80%)',
        'optimal_ph': '6.0 - 7.5 (Alluvial deltaic soil)',
        'ideal_temp': '24 - 37°C',
        'economic_yield': '2.8 - 4.2 tonnes dry fiber / ha',
        'fertilizer_tips': 'High Nitrogen requirement (60-80 kg/ha) for rapid vegetative stem elongation. Apply in 2 split top dressings.',
        'pest_control': 'Yellow mite and Jute semilooper. Clean retting water is essential for golden fiber quality.',
        'companion_crops': 'Rice in rotation, Mustard after harvest.',
        'icon': 'bi-align-middle',
        'accent_color': '#B5838D'
    },
    'coffee': {
        'display_name': 'Coffee (Arabica / Robusta)',
        'category': 'Plantation Beverage',
        'season': 'Perennial Shade-Grown',
        'duration_days': 'Perennial (Berry ripening takes 8-9 months)',
        'water_need': 'High (150 - 250 cm, blossom showers critical)',
        'optimal_ph': '5.0 - 6.5 (Acidic forest humus)',
        'ideal_temp': '15 - 28°C',
        'economic_yield': '1.0 - 2.2 tonnes clean bean / ha',
        'fertilizer_tips': 'Requires rich organic matter. Apply lime/dolomite if pH falls below 5.0. Split NPK applications before and after monsoons.',
        'pest_control': 'Coffee Berry Borer and White Stem Borer. Maintain 40-50% filtered canopy shade.',
        'companion_crops': 'Black pepper on shade trees, Cardamom, Orange intercrops.',
        'icon': 'bi-cup-hot-fill',
        'accent_color': '#6F4E37'
    }
}

# Regional presets for demo and presentation
REGIONAL_PRESETS = [
    {
        'id': 'punjab',
        'name': 'Punjab Plains (Rice / Wheat Belt)',
        'desc': 'Alluvial soil, high nitrogen, canal irrigation, monsoon climate',
        'N': 90, 'P': 42, 'K': 43, 'temp': 24.5, 'humidity': 80.0, 'ph': 6.5, 'rainfall': 210.0,
        'expected_crop': 'rice'
    },
    {
        'id': 'kerala',
        'name': 'Kerala Coastal Plantation',
        'desc': 'High rainfall, tropical humidity, coastal sandy-loam with rich potash',
        'N': 20, 'P': 25, 'K': 30, 'temp': 27.2, 'humidity': 92.5, 'ph': 5.8, 'rainfall': 225.0,
        'expected_crop': 'coconut'
    },
    {
        'id': 'coorg',
        'name': 'Coorg Highlands (Coffee Estate)',
        'desc': 'Cool tropical hill climate, acidic humus soil, high rainfall',
        'N': 105, 'P': 30, 'K': 32, 'temp': 23.5, 'humidity': 65.0, 'ph': 6.2, 'rainfall': 160.0,
        'expected_crop': 'coffee'
    },
    {
        'id': 'rajasthan',
        'name': 'Rajasthan Arid Belt (Mothbeans / Pulses)',
        'desc': 'High temperature, dry climate, alkaline sandy soil, minimal water',
        'N': 15, 'P': 55, 'K': 20, 'temp': 31.0, 'humidity': 48.0, 'ph': 7.2, 'rainfall': 45.0,
        'expected_crop': 'mothbeans'
    },
    {
        'id': 'kashmir',
        'name': 'Kashmir Apple Valley',
        'desc': 'Temperate cool mountain climate, moderate moisture, acidic loam',
        'N': 22, 'P': 135, 'K': 200, 'temp': 21.0, 'humidity': 91.0, 'ph': 6.0, 'rainfall': 110.0,
        'expected_crop': 'apple'
    },
    {
        'id': 'maharashtra',
        'name': 'Maharashtra Cotton Vertisol',
        'desc': 'Deep black soil, high potash, warm sun, moderate rain',
        'N': 115, 'P': 45, 'K': 20, 'temp': 24.0, 'humidity': 78.0, 'ph': 6.9, 'rainfall': 80.0,
        'expected_crop': 'cotton'
    }
]

# Benchmark accuracy comparison across all 7 trained algorithms
MODEL_BENCHMARKS = [
    {'name': 'Random Forest', 'accuracy': 99.55, 'f1': 0.995, 'type': 'Ensemble Bagging', 'winner': True},
    {'name': 'Gradient Boosting', 'accuracy': 99.09, 'f1': 0.991, 'type': 'Ensemble Boosting', 'winner': False},
    {'name': 'Support Vector Machine (SVM)', 'accuracy': 97.73, 'f1': 0.978, 'type': 'Kernel Classifier', 'winner': False},
    {'name': 'Gaussian Naive Bayes', 'accuracy': 99.32, 'f1': 0.993, 'type': 'Probabilistic', 'winner': False},
    {'name': 'Decision Tree', 'accuracy': 98.64, 'f1': 0.986, 'type': 'Tree Model', 'winner': False},
    {'name': 'K-Nearest Neighbors', 'accuracy': 97.50, 'f1': 0.975, 'type': 'Instance-based', 'winner': False},
    {'name': 'Logistic Regression', 'accuracy': 95.23, 'f1': 0.951, 'type': 'Linear Classifier', 'winner': False}
]

def get_crop_info(crop_name):
    """Safely retrieves agronomic dossier for a crop."""
    key = str(crop_name).lower().strip()
    return CROP_PROFILES.get(key, {
        'display_name': crop_name.capitalize(),
        'category': 'Agricultural Crop',
        'season': 'General Growing Season',
        'duration_days': '90 - 120 days',
        'water_need': 'Moderate',
        'optimal_ph': '6.0 - 7.5',
        'ideal_temp': '20 - 30°C',
        'economic_yield': 'Standard market yield',
        'fertilizer_tips': 'Apply balanced N-P-K fertilizer based on soil testing.',
        'pest_control': 'Practice integrated pest management (IPM) and crop rotation.',
        'companion_crops': 'Legumes and local cover crops.',
        'icon': 'bi-flower1',
        'accent_color': '#3F7A45'
    })

def _ask_gemini_agronomist(question, profile, current_metrics, chat_history):
    """Queries Google Gemini LLM for deep agronomic reasoning when GEMINI_API_KEY is configured."""
    gemini_key = os.environ.get('GEMINI_API_KEY', '').strip()
    if not gemini_key:
        return None

    try:
        import requests
        system_instruction = (
            "You are OptiBot, an expert precision agronomist AI assistant embedded in the OptiCrop platform. "
            "You provide actionable, scientifically sound agricultural advice on soil nutrients (N, P, K), "
            "crop rotation, irrigation schedules, pest management, and farming economics. "
            "Keep your answers concise, practical, and formatted cleanly with markdown bullet points and emojis."
        )

        context_summary = f"Current Target Crop: {profile['display_name']} ({profile['category']})\n"
        context_summary += f"- Season: {profile['season']}\n"
        context_summary += f"- Lifecycle: {profile['duration_days']}\n"
        context_summary += f"- Water Need: {profile['water_need']}\n"
        context_summary += f"- Optimal Soil pH: {profile['optimal_ph']}\n"
        context_summary += f"- Ideal Temperature: {profile['ideal_temp']}\n"
        context_summary += f"- Fertilizer Protocols: {profile['fertilizer_tips']}\n"
        context_summary += f"- Pest Management: {profile['pest_control']}\n"

        if current_metrics:
            context_summary += (
                f"\nCalibrated Soil & Ambient Parameters:\n"
                f"Nitrogen (N): {current_metrics.get('N')} kg/ha, "
                f"Phosphorus (P): {current_metrics.get('P')} kg/ha, "
                f"Potassium (K): {current_metrics.get('K')} kg/ha, "
                f"Temperature: {current_metrics.get('temperature')}°C, "
                f"Humidity: {current_metrics.get('humidity')}%, "
                f"pH: {current_metrics.get('ph')}, "
                f"Rainfall: {current_metrics.get('rainfall')} mm\n"
            )

        contents = []
        if chat_history:
            for msg in chat_history[-6:]:
                role = 'user' if msg.get('role') == 'user' else 'model'
                contents.append({
                    'role': role,
                    'parts': [{'text': msg.get('content', '')}]
                })

        prompt_with_context = f"[AGRONOMIC CONTEXT]\n{context_summary}\n\nFarmer Question: {question}"
        contents.append({
            'role': 'user',
            'parts': [{'text': prompt_with_context}]
        })

        payload = {
            'system_instruction': {
                'parts': [{'text': system_instruction}]
            },
            'contents': contents,
            'generationConfig': {
                'temperature': 0.4,
                'maxOutputTokens': 800
            }
        }

        for model in ['gemini-2.5-flash', 'gemini-1.5-flash']:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={gemini_key}"
                resp = requests.post(url, json=payload, timeout=8)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get('candidates', [])
                    if candidates:
                        parts = candidates[0].get('content', {}).get('parts', [])
                        if parts and 'text' in parts[0]:
                            return parts[0]['text'].strip()
            except Exception:
                continue
    except Exception:
        pass

    return None


def ask_agronomist_bot(question, current_crop=None, current_metrics=None, chat_history=None):
    """
    Intelligent OptiBot agronomist response engine.
    Uses Google Gemini LLM when GEMINI_API_KEY is configured,
    with automatic fallback to built-in agronomic domain rules.
    """
    crop = (current_crop or 'general').lower()
    profile = get_crop_info(crop)

    # 1. Attempt Extended Knowledge reasoning via Google Gemini
    llm_response = _ask_gemini_agronomist(question, profile, current_metrics, chat_history)
    if llm_response:
        return llm_response

    # 2. Built-in domain rule engine fallback
    q = question.lower()
    
    # Check for fertilizer & nutrient inquiries
    if any(w in q for w in ['fertilizer', 'nitrogen', 'phosphorus', 'potassium', 'urea', 'dap', 'npk']):
        if current_metrics and current_metrics.get('N', 0) < 40:
            return (f"🌱 **Nutrient Advisory for {profile['display_name']}**:\n\n"
                    f"Your soil Nitrogen level is on the lower side ({current_metrics.get('N')} kg/ha). "
                    f"For {profile['display_name']}, consider applying Neem-coated Urea or organic vermicompost. "
                    f"Recommended guideline: {profile['fertilizer_tips']}")
        return (f"🌿 **Fertilizer Guidance for {profile['display_name']}**:\n\n"
                f"{profile['fertilizer_tips']}\n\n"
                f"💡 *Pro-Tip*: Maintain a balanced N:P:K ratio and test soil organic carbon every two seasons.")

    # Check for water, irrigation, or rainfall questions
    if any(w in q for w in ['water', 'irrigation', 'rainfall', 'rain', 'dry', 'flood']):
        return (f"💧 **Water & Irrigation Scheduling for {profile['display_name']}**:\n\n"
                f"• **Requirement**: {profile['water_need']}\n"
                f"• **Optimal Season**: {profile['season']}\n"
                f"• **Best Practice**: Use drip irrigation or micro-sprinklers where possible to maximize Water Use Efficiency (WUE) and prevent waterlogging.")

    # Check for why this crop was recommended
    if any(w in q for w in ['why', 'reason', 'recommend', 'how did you choose', 'accuracy']):
        metric_str = ""
        if current_metrics:
            metric_str = f"with N={current_metrics.get('N')}, P={current_metrics.get('P')}, K={current_metrics.get('K')}, Temp={current_metrics.get('temperature')}°C, and Rainfall={current_metrics.get('rainfall')}mm"
        return (f"🎯 **Why {profile['display_name']} was chosen**:\n\n"
                f"Our Random Forest ensemble model (99.5% accuracy) evaluated your 7 environmental metrics {metric_str}. "
                f"These conditions closely mirror the ideal physiological envelope for {profile['display_name']} "
                f"(Optimal pH: {profile['optimal_ph']}, Ideal Temp: {profile['ideal_temp']}, Cycle: {profile['duration_days']}). "
                f"It offers the highest yield probability compared to other candidates.")

    # Check for pests, diseases, insects
    if any(w in q for w in ['pest', 'disease', 'insect', 'fungus', 'spray', 'bug', 'worm']):
        return (f"🛡️ **Plant Protection & IPM for {profile['display_name']}**:\n\n"
                f"{profile['pest_control']}\n\n"
                f"Always adopt Integrated Pest Management (IPM): install pheromone traps early and prefer bio-pesticides over broad-spectrum chemical sprays.")

    # Check for profit, money, yield, harvest, economics
    if any(w in q for w in ['yield', 'profit', 'money', 'economic', 'harvest', 'sell', 'market', 'duration']):
        return (f"📊 **Economic & Harvest Outlook for {profile['display_name']}**:\n\n"
                f"• **Maturity Cycle**: {profile['duration_days']}\n"
                f"• **Estimated Yield**: {profile['economic_yield']}\n"
                f"• **Companion Crops**: {profile['companion_crops']}\n"
                f"Planning your harvest to align with peak wholesale market windows can boost profit margins by up to 25%.")

    # Check for rotation, companion, intercrop
    if any(w in q for w in ['rotation', 'companion', 'intercrop', 'next crop', 'after this']):
        return (f"🔄 **Crop Rotation & Companion Planting**:\n\n"
                f"For {profile['display_name']}, the ideal companion and rotation choices are:\n"
                f"• {profile['companion_crops']}\n\n"
                f"Rotating with nitrogen-fixing pulses (like Chickpea, Mungbean, or Lentil) restores soil vitality and breaks pest breeding cycles naturally.")

    # General fallback response
    return (f"🌾 **OptiBot Agronomy Assistant**:\n\n"
            f"I am actively monitoring your plot data for **{profile['display_name']}** ({profile['category']}).\n"
            f"You can ask me about:\n"
            f"1. *'What fertilizer should I apply?'*\n"
            f"2. *'How much water is needed?'*\n"
            f"3. *'Why was {profile['display_name']} chosen over other crops?'*\n"
            f"4. *'What pests should I watch out for?'*\n"
            f"5. *'What are the best companion or rotation crops?'*")

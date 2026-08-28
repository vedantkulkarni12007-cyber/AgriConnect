// =============================================================
// Crop and Produce Visual Assets Map
// Provides high-quality, authentic agricultural imagery for crops
// =============================================================

export const CROP_IMAGES = {
  Onion: '/images/crop-onion.jpeg',
  Tomato: '/images/crop-tomato.webp',
  Wheat: '/images/crop-wheat.jpg',
  Rice: '/images/crop-rice.jpg',
  Potato: '/images/crop-potato.jpeg',
  Soybean: '/images/crop-soybean.svg',
  Cotton: '/images/crop-cotton.svg',
  Maize: '/images/crop-maize.svg',
  Chilli: '/images/crop-chilli.svg',
};

// Fallback icon/image if a crop is not in the map
export const getCropImage = (cropName) => {
  if (!cropName) return CROP_IMAGES.Wheat;
  const normalized = Object.keys(CROP_IMAGES).find(
    (k) => k.toLowerCase() === cropName.toLowerCase()
  );
  return normalized ? CROP_IMAGES[normalized] : CROP_IMAGES.Wheat;
};

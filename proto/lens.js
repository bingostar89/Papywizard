f.utilization = 100 // %

// Calculate hypothenuse of the image
function calculatediam(f) {
    with(Math)
    f.diam.value = round(100 * (sqrt((pow(f.length.value, 2)) + (pow(f.width.value, 2))))) / 100
}

// Calculate field of view of normal lens using the entered image length
function calculateNormFOVlength(f) {
    with(Math)
    f.NormFOVlength.value = (round(100 * ((360 / PI) * (atan((f.utilization.value / 100.0 * f.length.value) / (2 * f.focalLength.value)))))) / 100
}

// Calculate field of view of fisheye lens using the entered image length
function calculateFishFOVlength(f) {
    with(Math)
    f.FishFOVlength.value = (round(100 * ((360 / PI) * (asin(((f.utilization.value / 100 * f.length.value) / 2) / (2 * f.focalLength.value))) * 2))) / 100
}

// Calculate field of view of normal lens using the entered image width
function calculateNormFOVwidth(f) {
    with(Math)
    f.NormFOVwidth.value = (round(100 * ((360 / PI) * (atan((f.utilization.value / 100.0 * f.width.value) / (2 * f.focalLength.value)))))) / 100
}

// Calculate field of view of fisheye lens using the entered image width
function calculateFishFOVwidth(f) {
    with(Math)
    f.FishFOVwidth.value = (round(100 * ((360 / PI) * (asin(((f.utilization.value / 100 * f.width.value) / 2) / (2 * f.focalLength.value))) * 2))) / 100
}

// Calculate diagonal field of view of normal lens using the calculated image hypothenuse
function calculateNormFOVdiam(f) {
    with(Math)
    f.NormFOVdiam.value = (round(100 * ((360 / PI) * (atan((f.utilization.value / 100.0 * f.diam.value) / (2 * f.focalLength.value)))))) / 100
}

// Calculate diagonal field of view of fisheye lens using the calculated image hypothenuse
function calculateFishFOVdiam(f) {
    with(Math)
    f.FishFOVdiam.value = (round(100 * ((360 / PI) * (asin(((f.utilization.value / 100 * f.diam.value) / 2) / (2 * f.focalLength.value))) * 2))) / 100
}

// Calculate the number of images needed with the fiheye lens to
// reach the entered field of view using the entered overlap and
// landscape orientation
// Overlap is calculated as a percentage of the field of view
function calculateFishImNrLandscape(f) {
    with(Math)
    f.FishImNrLandscape.value = round(10 * (f.FishDesPanAngle.value / (f.FishFOVlength.value - ((f.FishOverlap.value / 100) * f.FishFOVlength.value)))) / 10
}

// Calculate the number of images needed with the fiheye lens to
// reach the entered field of view using the entered overlap and
// portrait orientation
// Overlap is calculated as a percentage of the field of view
function calculateFishImNrPortrait(f) {
    with(Math)
    f.FishImNrPortrait.value = round(10 * (f.FishDesPanAngle.value / (f.FishFOVwidth.value - ((f.FishOverlap.value / 100) * f.FishFOVwidth.value)))) / 10
}

// Calculate the number of images needed with the normal lens to
// reach the entered field of view using the entered overlap and
// landscape orientation
// Overlap is calculated as a percentage of the field of view
function calculateNormImNrLandscape(f) {
    with(Math)
    f.NormImNrLandscape.value = round(10 * (f.NormDesPanAngle.value / (f.NormFOVlength.value - ((f.NormOverlap.value / 100) * f.NormFOVlength.value)))) / 10
}

// Calculate the number of images needed with the normal lens to
// reach the entered field of view using the entered overlap and
// landscape orientation
// Overlap is calculated as a percentage of the field of view
function calculateNormImNrPortrait(f) {
    with(Math)
    f.NormImNrPortrait.value = round(10 * (f.NormDesPanAngle.value / (f.NormFOVwidth.value - ((f.NormOverlap.value / 100) * f.NormFOVwidth.value)))) / 10
}

// Calculate the percentage of overlap using a fisheye lens and
// the entered number of images in portrait orientation
// Overlap is a percentage of the field of view
function calculateFishOverlapPo(f) {
    with(Math)
    f.FishOverlapPo.value = round(100 * (((f.FishGivenNrImages.value * f.FishFOVwidth.value) - f.FishDesPanAngle.value) / f.FishGivenNrImages.value) / f.FishFOVwidth.value)
}

// Calculate the percentage of overlap using a fisheye lens and
// the entered number of images in landscape orientation
// Overlap is a percentage of the field of view
function calculateFishOverlapLa(f) {
    with(Math)
    f.FishOverlapLa.value = round(100 * (((f.FishGivenNrImages.value * f.FishFOVlength.value) - f.FishDesPanAngle.value) / f.FishGivenNrImages.value) / f.FishFOVlength.value)
}

// Calculate the number of images needed with the normal lens
// to reach the entered field of view using the entered overlap
// and portrait orientation-->
// Overlap is calculated as a percentage of the field of view
function calculateNormOverlapPo(f) {
    with(Math)
    f.NormOverlapPo.value = round(100 * (((f.NormGivenNrImages.value * f.NormFOVwidth.value) - f.NormDesPanAngle.value) / f.NormGivenNrImages.value) / f.NormFOVwidth.value)
}

// Calculate the percentage of overlap using a normal lens and
// the entered number of images in landscape orientation
// Overlap is a percentage of the field of view
function calculateNormOverlapLa(f) {
    with(Math)
    f.NormOverlapLa.value = round(100 * (((f.NormGivenNrImages.value * f.NormFOVlength.value) - f.NormDesPanAngle.value) / f.NormGivenNrImages.value) / f.NormFOVlength.value)
}

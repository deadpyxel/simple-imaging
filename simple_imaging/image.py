from __future__ import annotations

import copy
from typing import Generator

from .errors import ImcompatibleImages
from .errors import ValidationError
from .types import GrayPixel
from .types import Pixel
from .types import RGBPixel
from .utils import get_split_strings
from .utils import parse_file_contents

# TODO: Reaplce this Dictionary with a Enum
# source: https://en.wikipedia.org/wiki/Kernel_(image_processing)#Edge_Handling
KERNEL_FILTERS = {
    "identity": (0, 0, 0, 0, 1, 0, 0, 0, 0),
    "edge": (1, 0, -1, 0, 0, 0, -1, 0, 1),
    "laplace": (0, -1, 0, -1, 4, -1, 0, -1, 0),
    "laplace2": (-1, -1, -1, -1, 8, -1, -1, -1, -1),
    "sharpen": (0, -1, 0, -1, 5, -1, 0, -1, 0),
    "box_blur": (
        0.1111,
        0.1111,
        0.1111,
        0.1111,
        0.1111,
        0.1111,
        0.1111,
        0.1111,
        0.1111,
    ),
    "gaussian_blur": (
        0.0625,
        0.125,
        0.0625,
        0.125,
        0.25,
        2,
        0.0625,
        0.125,
        0.0625,
    ),
    "emboss": (-2, -1, 0, -1, 1, 1, 0, 1, 2),
}


def read_file(filepath: str) -> Image:
    """File reading utility

    Given a file path, attempts to validade file contents,
    if said contents are valid, returns an Image object


    Arguments:
        filepath {str} -- path for desired Netpbm file

    Returns:
        Image -- Image object generated by the file contents
    """
    image = Image.from_file(filepath)
    return image


def save_file(filepath: str, image: Image) -> None:
    """Writes image to disk

    Args:
        filepath (str): the path to write the file too
        image (Image): an Image object to be written
    """
    with open(filepath, "w") as f:
        f.write(f"{image.header}\n")
        f.write(f"{image.x} {image.y}\n")
        f.write(f"{image.max_level}\n")
        if image.header == "P3":
            pixel_data = []
            for line in image.values:
                pixel_line = []
                for pixel in line:
                    pixel_line.extend(pixel.value)
                pixel_data.extend(pixel_line)
        else:
            pixel_data = []
            for line in image.values:
                p_line = " ".join([str(pixel.value) for pixel in line])
                pixel_data.append(p_line)
        str_line = "\n".join(line for line in pixel_data)
        f.writelines(f"{str_line}")


def extract_channels(img: Image) -> list[Image, Image, Image]:
    """Extracts the RGB channels from a P3 image

    Args:
        img (Image): a P3 Image

    Returns:
        list[Image, Image, Image]: a list where each element is a channel in the RGB Image
    """    
    # Split each channel into a separated value list.
    red_channel = [[GrayPixel(pixel.red) for pixel in row] for row in img.values]
    green_channel = [[GrayPixel(pixel.green) for pixel in row] for row in img.values]
    blue_channel = [[GrayPixel(pixel.blue) for pixel in row] for row in img.values]
    # Instantiate each channel as a new P2 (Grayscale) Image
    r_channel_image = Image(
        header="P2",
        max_level=img.max_level,
        dimensions=(img.x, img.y),
        contents=red_channel,
    )
    g_channel_image = Image(
        header="P2",
        max_level=img.max_level,
        dimensions=(img.x, img.y),
        contents=blue_channel,
    )
    b_channel_image = Image(
        header="P2",
        max_level=img.max_level,
        dimensions=(img.x, img.y),
        contents=green_channel,
    )

    return [r_channel_image, g_channel_image, b_channel_image]


def merge_channels(channels: list[Image, Image, Image]) -> Image:
    """Merges 3 P2 images into one RGB image

    Args:
        channels (list[Image, Image, Image]): input images, each corresponding to a channel in the RGB model

    Returns:
        Image: a composite P3 Image
    """    
    # Grabs only the channel data
    r_channel, g_channel, b_channel = (
        channels[0].values,
        channels[1].values,
        channels[2].values,
    )
    rgb_channels = [
        [RGBPixel(r.value, g.value, b.value) for r, g, b in row]
        for row in zip(r_channel, g_channel, b_channel)
    ]
    for row in zip(r_channel, g_channel, b_channel):
        print(f"{row=}")
        for r, g, b in row:
            print(f"{r=} {g=} {b=}")
    base_image = channels[0]
    return Image(
        header="P3",
        max_level=base_image.max_level,
        dimensions=(base_image.x, base_image.y),
        contents=rgb_channels,
    )


def validate_image_compatibility(image1: Image, image2: Image) -> bool:
    """Validates the compatibility between two images
    
    Returns:
        bool: True if the images are compatible
    """    
    return (
        # same dimensions
        (image1.x, image1.y)
        == (
            image2.x,
            image2.y,
        )
        # same header
        and image1.header == image2.header
        # same max_level for colors
        and image1.max_level == image2.max_level
    )


def _map_value(input_value: int) -> float:
    return input_value / 255.0


def _calculate_frequencies(
    histogram: dict[str, int], pixel_total: int
) -> dict[str, float]:
    """Sumarizes the frequencies for a given histogram

    Args:
        histogram (dict[str, int]): dictionary where each key is a pixel value
        and each value is an integer
        pixel_total (int): total number of pixels in the image

    Returns:
        dict[str, float]: a dictionary where for each pixel(key) there's a
        corresponding float value for the frequence
    """
    return {k: v / pixel_total for k, v in histogram.items()}


def _generate_equalized_map(
    frequencies: dict[str, float], num_level: int
) -> dict[str, int]:
    """Given a dictionary of frequencies, generates the equalized map for those frequencis

    Args:
        frequencies (dict[str, float]): a dict where each graylevel (key) has a corresponding frequency (value)
        num_level (int): number of graylevels in the image

    Returns:
        dict[str, int]: equalized map of values where each level (key) has a corresponding new intensity (value)
    """
    cummulative_freq = 0.0  # cumulative frequence of each gray level
    equalized_map = {}  # the map that will hold the resulting values
    # Calculate the mapped output for each level
    for level, freq in frequencies.items():
        cummulative_freq += freq
        resulting_value = round((num_level - 1) * cummulative_freq)
        equalized_map[level] = resulting_value
    return equalized_map


class Image:
    def __init__(
        self,
        header: str,
        max_level: int,
        dimensions: tuple[int, int],
        contents: list[list[Pixel]] = None,
    ):
        """Image class

        Args:
            header (str): A string of the image header, accepts (P1, P2 and P3)
            max_level (int): Max number of gray levels allowed for the image
            dimensions (tuple[int, int]): The (width, height) dimensions of the image
            contents (list[list[Pixel]], optional): A Pixel matrix to pre-populate the iamge. Defaults to None.

        Raises:
            ValidationError: If there're invalid dimensions (below 0, None)
        """
        if any(i <= 0 for i in dimensions):
            raise ValidationError(
                "An Image cannot have any dimension negative or null."
            )
        self.header = header
        self.x, self.y = dimensions
        self.max_level = max_level
        self.values = contents

    @classmethod
    def from_file(cls, filepath: str) -> Image:
        """Creates image from file

        Args:
            filepath (str): path to source file
        """
        with open(filepath) as f:
            f_contents = get_split_strings(f)
        image_data = parse_file_contents(f_contents)
        image = cls(**image_data)
        return image

    @property
    def dimensions(self):
        return (self.x, self.y)

    def copy_current_image(self) -> Image:
        """Creates a deepcopy of the current image

        Returns:
            Image: copy (full copy) of the current image data
        """        
        return copy.deepcopy(self)

    def negative(self, inplace: bool = True) -> Image:
        """Negative operation

        For each pixel in the image, invokes the Pixel `negative` method

        Args:
            inplace (bool, optional): Controls if the result will be a new Image. Defaults to True.

        Returns:
            Image: Processing result
        """        
        for line in self.values:
            for pixel in line:
                pixel.negative()
        return self if inplace else self.copy_current_image()

    def add_image(self, other_image: Image, inplace: bool = True) -> Image:
        """Image addition

        Given two compatible images, realizes the addition of each corresponding pixel
        
        Args:
            other_image (Image): image to be added
            inplace (bool, optional): If False will generate a new image as result. Defaults to True.

        Raises:
            ImcompatibleImages: If the images are incompatible (mismatching dimensions or headers)

        Returns:
            Image: processing result
        """        
        if not validate_image_compatibility(self, other_image):
            raise ImcompatibleImages(
                "The images are incompatible for the `add` operation"
            )

        value_list = other_image.values
        pixel_data = self._generate_working_copy(populate=True)
        for i, line in enumerate(value_list):
            for j, pixel in enumerate(line):
                pixel_data[i][j] += pixel
        return self._return_result(pixel_data, inplace)

    def subtract_image(self, other_image: Image, inplace: bool = True) -> Image:
        """Image subtraction

        Given two compatible images, realizes the subtraction of each corresponding pixel
        
        Args:
            other_image (Image): image to be subtracted
            inplace (bool, optional): If False will generate a new image as result. Defaults to True.

        Raises:
            ImcompatibleImages: If the images are incompatible (mismatching dimensions or headers)

        Returns:
            Image: processing result
        """  
        if not validate_image_compatibility(self, other_image):
            raise ImcompatibleImages(
                "The images are incompatible for the `subtract` operation"
            )

        value_list = other_image.values
        pixel_data = self._generate_working_copy(populate=True)
        for i, line in enumerate(value_list):
            for j, pixel in enumerate(line):
                pixel_data[i][j] -= pixel
        return self._return_result(pixel_data, inplace)

    def multiply_image(self, value: int, inplace: bool = True) -> Image:
        """Image multiplication by an integer

        Given an integer value, realizes the pixel-wise multiplication of the value
        
        Args:
            value (int): integer to multiply the image by
            inplace (bool, optional): If false will generate a new image as result. Defaults to True.
            
        Returns:
            Image: processing result
        """  
        pixel_matrix = self._generate_working_copy(populate=True)
        for row in pixel_matrix:
            for pixel in row:
                pixel *= value
        return self._return_result(pixel_matrix, inplace)

    def high_boost_filter(self, k: int | float = 1, inplace: bool = True) -> Image:
        """Applies the High-Boost filter

        Args:
            k (int, optional): adjustment constant. Defaults to 1.
            inplace (bool, optional): If false will generate a new image as result. Defaults to True.

        Returns:
            Image: processing result
        """        
        img_copy = self.copy_current_image()  # create working copy
        # blur image using median filter 3x3
        blurred_image = self.median_filter(kernel=3, inplace=False)
        # create a mask by subtracting the blur from the "original"
        mask = img_copy.subtract_image(blurred_image, inplace=True)
        # result is the current image added to the mask mutiplied by a K constant
        return self.add_image(mask.multiply_image(k), inplace)

    def average_filter(self, kernel: int, inplace: bool = True) -> Image:
        """Average filtering

        Given a kernel size this method will get the arithmetic average of the 
        pixels in a sliding window and apply the result to the pivot (central) pixel.

        Args:
            kernel (int): kernel size. a kernel of 3 will result in a sliding window of 3x3 pixels.
            inplace (bool, optional): If false will generate a new image as result. Defaults to True.

        Returns:
            Image: processing result
        """        
        coord_list = [(i, j) for i in range(self.y) for j in range(self.x)]
        pixel_data = self._generate_working_copy()
        for sw, (i, j) in zip(self._sliding_window(size=kernel), coord_list):
            flattened_values = [value for line in sw for value in line]
            avg_value = round(sum(flattened_values) / (kernel * kernel))
            pixel_data[i][j] = GrayPixel(max(0, min(255, avg_value)))
        return self._return_result(pixel_data, inplace)

    def median_filter(self, kernel: int, inplace: bool = True) -> Image:
        """Median filtering

        Given a kernel size this method will get the median of the ordered list 
        of pixels in a sliding window and apply the result to the pivot (central) pixel.

        Args:
            kernel (int): kernel size. a kernel of 3 will result in a sliding window of 3x3 pixels.
            inplace (bool, optional): If false will generate a new image as result. Defaults to True.

        Returns:
            Image: processing result
        """       
        coord_list = [(i, j) for i in range(self.y) for j in range(self.x)]
        pixel_data = self._generate_working_copy()
        for sw, (i, j) in zip(self._sliding_window(size=kernel), coord_list):
            flattened_values = sorted([value for line in sw for value in line])
            l_size = len(flattened_values)
            if l_size % 2 != 0:
                pixel_data[i][j] = GrayPixel(flattened_values[l_size // 2])
            else:
                pixel_data[i][j] = GrayPixel(flattened_values[l_size // 2 - 1])

        return self._return_result(pixel_data, inplace)

    def laplacian_filter(self, inplace: bool = True) -> Image:
        """Applies the laplacian filter to the image

        Args:
            inplace (bool, optional): If false will generate a new image as result. Defaults to True.

        Returns:
            Image: processing result
        """        
        return self._kernel_filter(inplace=inplace)

    def _kernel_filter(self, kernel: str = "laplace", inplace: bool = True) -> Image:
        """Abstract kernel filtering method

        given a selection of predefined kernels, this method will apply that kernel to
        the image.

        Current predefined options are:
            - identity
            - edge
            - laplace
            - laplace2
            - box_blur
            - gaussian_blur
            - sharpen
            - emboss

        Args:
            kernel (str, optional): The kernel to be utilized. Defaults to "laplace".
            inplace (bool, optional): If false will generate a new image as result. Defaults to True.

        Raises:
            ValidationError: if the passed kernel is not defined.

        Returns:
            Image: processing result
        """        
        try:
            kernel_filter = KERNEL_FILTERS[kernel]
        except KeyError:
            raise ValidationError(
                f"Selected kernel is invalid, options are {KERNEL_FILTERS.keys()}"
            )
        coord_list = [(i, j) for i in range(self.y) for j in range(self.x)]
        pixel_data = self._generate_working_copy()
        for sw, (i, j) in zip(self._sliding_window(size=3), coord_list):
            flattened_sw = [val for line in sw for val in line]
            # process the result of the filtering process, clamping the value betwee [0, 255]
            result = max(
                0,
                min(
                    255,
                    round(
                        sum(
                            coef * val for coef, val in zip(kernel_filter, flattened_sw)
                        )
                    ),
                ),
            )
            pixel_data[i][j] = GrayPixel(result)

        return self._return_result(pixel_data, inplace)

    def gamma_transformation(
        self, gamma: float, c: int | float = 1, inplace: bool = True
    ) -> Image:
        """Gamma transformation

        Applies the gamma transformations processing in the image.
        Uses the formula `c * p ^ gamma`, where p is the current pixel value.

        Args:
            gamma (float): gamma value
            c (Union[int, float], optional): Adjustment constant. Defaults to 1.
            inplace (bool, optional): If the transformations should be inplace. Defaults to True.

        Returns:
            Image: [description]
        """
        # create a working copy from pixel data
        pixel_matrix = [[GrayPixel() for _ in range(self.x)] for _ in range(self.y)]
        for i, row in enumerate(self.values):
            for j, _ in enumerate(row):
                # map the pixel value to a 0~1 range
                current_value = _map_value(self.values[i][j].value)
                # calculate the gamma transformed value and reescale to 0~255 range
                gamma_value = round((255 * c) * (current_value ** gamma))
                # update the pixel value with the new transformed value,
                # respecting 0~255 range
                pixel_matrix[i][j] = GrayPixel(max(0, min(255, gamma_value)))
        return self._return_result(pixel_matrix, inplace)

    def histogram_equalization(self, inplace: bool = True) -> Image:
        """Does the global histogram equalization

        Args:
            inplace (bool, optional): If false will generate a new image as result. Defaults to True.

        Returns:
            Image: processing result
        """        
        hist = self.get_histogram()
        hist_frequencies = _calculate_frequencies(hist, self.x * self.y)
        eq_map = _generate_equalized_map(hist_frequencies, self.max_level)
        pixel_matrix = [[GrayPixel() for _ in range(self.x)] for _ in range(self.y)]
        for i, row in enumerate(self.values):
            for j, _ in enumerate(row):
                equalized_value = eq_map[str(self.values[i][j].value)]
                pixel_matrix[i][j] = GrayPixel(max(0, min(255, equalized_value)))
        return self._return_result(pixel_matrix, inplace)

    def _sliding_window(self, size: int) -> Generator[list[list[int]], None, None]:
        """Utility method for sliding window operations

        This method will slide a `size x size` window in the current matrix, 
        returning the current window in each step of the generator.

        This method uses the "extending" policy meaning that the border pixels 
        are virtually repeated for this process

        Args:
            size (int): the size of the sliding window

        Yields:
            Generator[list[list[int]], None, None]: a generator object that yields the current window
        """        
        offset = size // 2
        offset_coords = [
            (off_i, off_j)
            for off_i in range(-offset, offset + 1)
            for off_j in range(-offset, offset + 1)
        ]
        for i in range(0, self.y):
            for j in range(0, self.x):
                curr_window = [[0 for _ in range(size)] for _ in range(size)]
                for window_coord in offset_coords:
                    k, g = window_coord
                    p_i = i + k if 0 <= i + k < self.y else None
                    p_j = j + g if 0 <= j + g < self.x else None
                    if not (p_i is None or p_j is None):
                        curr_window[offset + k][offset + g] = self.values[p_i][
                            p_j
                        ].value
                    elif p_i is None and p_j is None:
                        curr_window[offset + k][offset + g] = self.values[i][j].value
                    elif p_i is None:
                        curr_window[offset + k][offset + g] = self.values[i][p_j].value
                    elif p_j is None:
                        curr_window[offset + k][offset + g] = self.values[p_i][j].value
                yield curr_window

    def local_histogram_equalization(self, kernel: int, inplace: bool = True) -> Image:
        """Local histogram euqalization

        Args:
            kernel (int): size of the window for the LHE process
            inplace (bool, optional): If false will generate a new image as result. Defaults to True.

        Returns:
            Image: processing result
        """        
        return NotImplemented

    def get_histogram(self, pixel_data: list[list[Pixel]] = None) -> dict[str, int]:
        """Generates the histogram for the image

        Args:
            pixel_data (list[list[Pixel]], optional): the pixel matrix to work on.
            Defaults to None. If None passed, will use the complete current image data.

        Raises:
            ValidationError: In case he image is not grayscale

        Returns:value
            dict[str, int]: histogram for image as a dictionary,
            where each key is the pixel value and each value is
            the number of courrences in the image
        """
        if self.header not in ("P1", "P2"):
            raise ValidationError("Cannot extract histogram of non-grayscale images")
        pixel_value_list = (
            [p.value for row in self.values for p in row]
            if pixel_data is None
            else [p.value for row in pixel_data for p in row]
        )
        # for each level, get the count of ocurrences in the pixel list
        hist = {str(i): pixel_value_list.count(i) for i in range(self.max_level + 1)}
        return hist

    def darken(self, level: int, inplace: bool = True) -> Image:
        """Darken image method

        Given a level in pixel value, this will darken the image by that much.
        The value must obey the criteria (0<=level<=255), else an Exception is raised

        Arguments:
            level {int} -- Pixel value (as in how much) for image enlightening
            inplace (bool, optional): If the operation should be executed in place. Defaults to True.

        Returns:
            Image: Resulting Image object from operation,
                    returns a copy if `inplace` is False
        """
        for i, row in enumerate(self.values):
            for j, _ in enumerate(row):
                self.values[i][j].darken(level)
        return self if inplace else self.copy_current_image()

    def lighten(self, level: int, inplace: bool = True) -> Image:
        """Lighten image method

        Given a level in pixel value, this will enlighten the image by that much.
        The value must obey the criteria (0<=level<=255), else an Exception is raised

        Arguments:
            level {int} -- Pixel value (as in how much) for image enlightening
            inplace (bool, optional): If the operation should be executed in place. Defaults to True.

        Returns:
            Image: Resulting Image object from operation,
                    returns a copy if `inplace` is False
        """
        for i, row in enumerate(self.values):
            for j, _ in enumerate(row):
                self.values[i][j].lighten(level)
        return self if inplace else self.copy_current_image()

    def binarization(self, threshold: int, inplace: bool = True) -> Image:
        """Binarization process

        Given a threshold (0 < threshold < 255), this operation wil set pixels
        below it to black and above it to white.

        Args:
            threshold (int): the level to split into white and black pixels
            inplace (bool, optional): Flag to set the opreationa s inplace. Defaults to True.

        Returns:
            Image: resulting process
        """
        pixel_matrix = self._generate_working_copy()
        for i, row in enumerate(self.values):
            for j, _ in enumerate(row):
                if self.values[i][j].value < threshold:
                    pixel_matrix[i][j] = GrayPixel(0)
                else:
                    pixel_matrix[i][j] = GrayPixel(255)
        return self._return_result(pixel_matrix, inplace)

    def highlight_band(
        self,
        threshold: tuple[int, int],
        intensity: int,
        intensity_outside: int | None = None,
        inplace: bool = True,
    ) -> Image:
        """Highlights an interval of pixels

        Args:
            threshold (tuple[int, int]): the interval of values to highlight, must obey (a < b) criteria
            intensity (int): the value to set those pixels that are inside the threshold
            intensity_outside (int, optional): the value to set pixels outside the threshold. Defaults to None.
            inplace (bool, optional): Controls the generation of a new image as result. Defaults to True.

        Raises:
            ValidationError: In case the threshold does not obey the criteria

        Returns:
            Image: the result of the processing
        """
        tr_min, tr_max = threshold
        if not all(isinstance(i, int) for i in (tr_min, tr_max)) or tr_min > tr_max:
            raise ValidationError(
                f"The threshold interval {threshold} contains invalid values. \
                    Should be a tuple of 2 integers, (a,b) where a < b."
            )
        # create a working copy from pixel data
        pixel_matrix = self._generate_working_copy()
        for i, row in enumerate(self.values):
            for j, _ in enumerate(row):
                if tr_min < self.values[i][j].value < tr_max:
                    pixel_matrix[i][j] = GrayPixel(intensity)
                # if we chose an intensity for the values outside of the
                # [A, B] interval
                elif intensity_outside is not None and isinstance(
                    intensity_outside, int
                ):
                    pixel_matrix[i][j] = GrayPixel(intensity_outside)
        return self._return_result(pixel_matrix, inplace)

    def rotate_90(self, clockwise: bool = True, inplace: bool = True) -> Image:
        """90 degree rotation

        Args:
            clockwise (bool, optional): defines the direction of rotation. Defaults to True.
            inplace (bool, optional): If false will generate a new image as result. Defaults to True.

        Returns:
            Image: processing result
        """        
        # This image MxN has to become NxM
        working_values = [[0 for _ in range(self.y)] for _ in range(self.x)]
        for i, row in enumerate(self.values):
            for j, pixel in enumerate(row):
                if not clockwise:
                    working_values[j][self.y - i - 1] = pixel
                else:
                    working_values[self.x - j - 1][i] = pixel
        self.x, self.y, self.values = self.y, self.x, working_values
        return self if inplace else self.copy_current_image()

    def rotate_180(self, inplace: bool = True) -> Image:
        """180 deegres rotation

        Args:
            inplace (bool, optional): If false will generate a new image as result. Defaults to True.

        Returns:
            Image: processing result
        """        
        for i, row in enumerate(self.values):
            for j, pixel in enumerate(row):
                self.values[self.x - i - 1][self.y - j - 1] = pixel
        return self if inplace else self.copy_current_image()

    def vertical_mirror(self, inplace: bool = True) -> Image:
        """Vertical mirroring operation

        Args:
            inplace (bool, optional): If false will generate a new image as result. Defaults to True.

        Returns:
            Image: processing result
        """        
        for i, row in enumerate(self.values):
            for j, pixel in enumerate(row):
                self.values[i][self.y - j - 1] = pixel
        return self if inplace else self.copy_current_image()

    def horizontal_mirror(self, inplace: bool = True) -> Image:
        """Horizontal Mirroring operation

        Args:
            inplace (bool, optional): If false will generate a new image as result. Defaults to True.

        Returns:
            Image: processing result
        """        
        for i, row in enumerate(self.values):
            for j, pixel in enumerate(row):
                self.values[self.x - i - 1][j] = pixel
        return self if inplace else self.copy_current_image()

    def set_pixel(self, x: int, y: int, pixel: Pixel) -> None:
        """Sets a pixel to a location

        Args:
            x (int): x position
            y (int): y position
            pixel (Pixel): pixel to replace the contents of that position

        Raises:
            ValidationError: if the location is outside the bound of the current image
        """        
        if not (0 < x <= self.x and 0 < y <= self.y):
            raise ValidationError(
                f"Tried to set_pixel on invalid position ({x}, {y}) on image ({self.x} x {self.y})"
            )
            # TODO: Validate pixel type
        self.values[x - 1][y - 1] = pixel

    def get_pixel(self, x: int, y: int) -> Pixel:
        """gets the pixel in a certain location

        Args:
            x (int): x position
            y (int): y position

        Raises:
            ValidationError: if the location is outside current image bounds.

        Returns:
            Pixel: the Pixel object at the desired location
        """        
        if not (0 < x <= self.x and 0 < y <= self.y):
            raise ValidationError(
                f"Tried to get_pixel on invalid position ({x}, {y}) on image ({self.x} x {self.y})"
            )
        return self.values[x - 1][y - 1]

    def _return_result(
        self, pixel_matrix: list[list[Pixel]], inplace: bool = True
    ) -> Image:
        """Utility method to handle the return of the processing result

        Args:
            pixel_matrix (list[list[Pixel]]): the processed pixel matrix
            inplace (bool, optional): If false will generate a new image as result. Defaults to True.

        Returns:
            Image: processing result
        """    
        if inplace:
            self.values = pixel_matrix
            return self
        else:
            return Image(
                header=self.header,
                max_level=self.max_level,
                dimensions=(self.x, self.y),
                contents=pixel_matrix,
            )

    def _generate_working_copy(self, populate: bool = False) -> list[list[Pixel]]:
        """Genertes a pixel matrix in the current image dimentions for processing

        Args:
            populate (bool, optional): If true will populate the matrix with the current values. Defaults to False.

        Returns:
            list[list[Pixel]]: a X * Y matrix of pixels
        """        
        if populate:
            return [
                [GrayPixel(self.values[j][i].value) for i in range(self.x)]
                for j in range(self.y)
            ]
        else:
            return [[GrayPixel() for _ in range(self.x)] for _ in range(self.y)]

    def __repr__(self):
        return f"{type(self).__name__}(header={self.header}, dim={self.dimensions})"

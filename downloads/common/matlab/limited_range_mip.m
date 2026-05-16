function [] = limited_range_mip(inputPath, outputDir, zRange, roi, xyPixelSize, zStepSize, writeCroppedStack)
%LIMITED_RANGE_MIP Create XY, XZ, YZ, and combined limited-z MIPs.
%
% inputPath: path to a 3D TIFF stack in Y, X, Z order after MATLAB loading.
% outputDir: directory where output TIFF files will be written.
% zRange: [firstZ, lastZ], one-based inclusive. Use [] for the full stack.
% roi: optional ImageJ/Fiji ROI [x, y, width, height]. Use [] for no crop.
% xyPixelSize: lateral pixel size.
% zStepSize: z-step size, in the same units as xyPixelSize.
% writeCroppedStack: optional true/false to write the cropped limited-z stack.

    if nargin < 7
        writeCroppedStack = false;
    end

    if ~exist(outputDir, 'dir')
        mkdir(outputDir);
    end

    [image, ~, ~, numberImages] = readtiffstack(inputPath);

    if ~isempty(zRange)
        if numel(zRange) ~= 2
            error('zRange must be [firstZ, lastZ] or [].');
        end
        if zRange(1) < 1 || zRange(2) < zRange(1) || zRange(2) > numberImages
            error('zRange must be one-based, inclusive, and within the stack.');
        end
        image = image(:, :, zRange(1):zRange(2));
    end

    if ~isempty(roi)
        if numel(roi) ~= 4
            error('roi must be [x, y, width, height] or [].');
        end
        x1 = roi(1) + 1;
        y1 = roi(2) + 1;
        x2 = x1 + roi(3) - 1;
        y2 = y1 + roi(4) - 1;
        if x1 < 1 || y1 < 1 || x2 > size(image, 2) || y2 > size(image, 1)
            error('ROI exceeds the image dimensions.');
        end
        image = image(y1:y2, x1:x2, :);
    end

    if xyPixelSize <= 0 || zStepSize <= 0
        error('xyPixelSize and zStepSize must be positive.');
    end
    zScale = zStepSize / xyPixelSize;

    mipXY = max(image, [], 3);
    mipXZ = scaleRows(squeeze(max(image, [], 1))', zScale, class(image));
    mipYZ = scaleRows(squeeze(max(image, [], 2))', zScale, class(image))';

    [~, stem, ~] = fileparts(inputPath);
    if isempty(zRange)
        suffix = 'full_stack';
    else
        suffix = sprintf('z%04d-%04d', zRange(1), zRange(2));
    end

    imwrite(mipXY, fullfile(outputDir, sprintf('%s_%s_mip_xy.tif', stem, suffix)));
    imwrite(mipXZ, fullfile(outputDir, sprintf('%s_%s_mip_xz.tif', stem, suffix)));
    imwrite(mipYZ, fullfile(outputDir, sprintf('%s_%s_mip_yz.tif', stem, suffix)));

    montage = zeros(size(mipXY, 1) + size(mipXZ, 1), size(mipXY, 2) + size(mipYZ, 2), class(image));
    montage(1:size(mipXY, 1), 1:size(mipXY, 2)) = mipXY;
    montage(size(mipXY, 1) + 1:end, 1:size(mipXZ, 2)) = mipXZ;
    montage(1:size(mipYZ, 1), size(mipXY, 2) + 1:end) = mipYZ;
    imwrite(montage, fullfile(outputDir, sprintf('%s_%s_mip_three.tif', stem, suffix)));

    if writeCroppedStack
        writetiffstack(image, fullfile(outputDir, sprintf('%s_%s_stack.tif', stem, suffix)));
    end
end

function scaled = scaleRows(image, scaleFactor, outputClass)
    if abs(scaleFactor - 1) < eps
        scaled = cast(image, outputClass);
        return;
    end

    oldRows = size(image, 1);
    newRows = max(1, round(oldRows * scaleFactor));
    [oldX, oldY] = meshgrid(1:size(image, 2), 1:oldRows);
    [newX, newY] = meshgrid(1:size(image, 2), linspace(1, oldRows, newRows));
    scaled = interp2(oldX, oldY, double(image), newX, newY, 'linear', 0);
    scaled = castToClass(scaled, outputClass);
end

function output = castToClass(image, outputClass)
    if startsWith(outputClass, 'uint') || startsWith(outputClass, 'int')
        limits = integerLimits(outputClass);
        image = min(max(round(image), limits(1)), limits(2));
    end
    output = cast(image, outputClass);
end

function limits = integerLimits(outputClass)
    switch outputClass
        case 'uint8'
            limits = [intmin('uint8'), intmax('uint8')];
        case 'uint16'
            limits = [intmin('uint16'), intmax('uint16')];
        case 'uint32'
            limits = [intmin('uint32'), intmax('uint32')];
        case 'uint64'
            limits = [intmin('uint64'), intmax('uint64')];
        case 'int8'
            limits = [intmin('int8'), intmax('int8')];
        case 'int16'
            limits = [intmin('int16'), intmax('int16')];
        case 'int32'
            limits = [intmin('int32'), intmax('int32')];
        case 'int64'
            limits = [intmin('int64'), intmax('int64')];
        otherwise
            limits = [-Inf, Inf];
    end
end

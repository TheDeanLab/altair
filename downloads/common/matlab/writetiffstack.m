%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
%           Function created by Bo-Jui Chang (bjo4), 2021/12/6 @ Dallas
%           Modified to support BigTIFF and dynamic data types
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [] = writetiffstack(image, path)

    [nx, ny, nz] = size(image);
    imgType = class(image);

    switch imgType
        case {'uint8', 'int8'}
            bitsPerSample = 8;
        case {'uint16', 'int16'}
            bitsPerSample = 16;
        case {'uint32', 'int32', 'single'}
            bitsPerSample = 32;
        case {'uint64', 'int64', 'double'}
            bitsPerSample = 64;
        otherwise
            bitsPerSample = 16;
    end

    bytesPerPixel = bitsPerSample / 8;
    estimatedSize = nx * ny * nz * bytesPerPixel;

    threshold = 4.0 * 1024^3;
    if estimatedSize > threshold
        tiffFile = Tiff(path, 'w8');
    else
        tiffFile = Tiff(path, 'w');
    end

    tagstruct.Photometric = Tiff.Photometric.MinIsBlack;
    tagstruct.ImageLength = nx;
    tagstruct.ImageWidth = ny;
    tagstruct.PlanarConfiguration = Tiff.PlanarConfiguration.Chunky;
    tagstruct.Compression = Tiff.Compression.None;
    tagstruct.BitsPerSample = bitsPerSample;

    if contains(imgType, 'int') && ~contains(imgType, 'uint')
        tagstruct.SampleFormat = Tiff.SampleFormat.Int;
    elseif contains(imgType, 'single') || contains(imgType, 'double')
        tagstruct.SampleFormat = Tiff.SampleFormat.IEEEFP;
    else
        tagstruct.SampleFormat = Tiff.SampleFormat.UInt;
    end

    for iz = 1:nz
        tiffFile.setTag(tagstruct);
        tiffFile.write(image(:, :, iz));
        if iz < nz
            tiffFile.writeDirectory();
        end
    end
    tiffFile.close();
end

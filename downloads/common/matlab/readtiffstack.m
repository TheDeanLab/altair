%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
%           Function created by Bo-Jui Chang (bjo4), 2021/12/6 @ Dallas
%           Modified to support BigTIFF and dynamic data types
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function [FinalImage, mImage, nImage, NumberImages] = readtiffstack(path)

    InfoImage = imfinfo(path);
    mImage = InfoImage(1).Height;
    nImage = InfoImage(1).Width;
    NumberImages = length(InfoImage);

    bitsPerSample = InfoImage(1).BitsPerSample;

    if isfield(InfoImage(1), 'SampleFormat')
        sampleFormat = InfoImage(1).SampleFormat;
    else
        sampleFormat = 1;
    end

    if sampleFormat == 3
        if bitsPerSample == 32
            dataType = 'single';
        else
            dataType = 'double';
        end
    elseif sampleFormat == 2
        if bitsPerSample == 8
            dataType = 'int8';
        elseif bitsPerSample == 16
            dataType = 'int16';
        elseif bitsPerSample == 32
            dataType = 'int32';
        else
            dataType = 'int64';
        end
    else
        if bitsPerSample == 8
            dataType = 'uint8';
        elseif bitsPerSample == 16
            dataType = 'uint16';
        elseif bitsPerSample == 32
            dataType = 'uint32';
        else
            dataType = 'uint64';
        end
    end

    FinalImage = zeros(mImage, nImage, NumberImages, dataType);

    warnState = warning('off', 'all');
    TifLink = Tiff(path, 'r');
    for i = 1:NumberImages
        TifLink.setDirectory(i);
        FinalImage(:, :, i) = TifLink.read();
    end
    TifLink.close();
    warning(warnState);
end

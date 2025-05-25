import { styled } from '@mui/material/styles'

export const MainDiv = styled('div', {
  shouldForwardProp: (prop) => ![
    'backgroundColor',
    'borderRadius',
    'borderColor',
    'borderWidth',
    'dragOver',
    'fontSize',
    'height',
    'width'].includes(prop)
})`
  ${({
    backgroundColor,
    borderRadius,
    borderColor,
    borderWidth,
    dragOver,
    fontSize,
    height,
    width,
  }) => (
    `
    align-items: center;
    background-color: ${backgroundColor};
    border: ${`${borderWidth} dashed ${borderColor}`};
    border-radius: ${`${borderRadius}`};
    box-shadow: ${dragOver ? `0 0 40px ${borderColor}` : 'none'};
    display: flex;
    justify-content: center;
    height: ${`${height}`};
    margin: 20px;
    width: ${`${width}`};

    & p {
      font-size: ${`${fontSize}`};
      cursor: default;
    }
    
    & .selectFilesDiv {
      padding: 15px 0px;
      height: 100%;
      width: 100%;
      & .clickableStack {
        justify-content: center;
        & * {
          cursor: pointer;
        }
        cursor: pointer;
        & p {
          font-weight: 600;
        }
      }
    }

    & .totalSize {
      font-weight: 600;
    }

    & .totalSizeStack {
      display: flex;
      align-items: center;
      justify-content: space-between;
      height: 100%;
      width: 100%;
    }
    
    & .totalSizeDiv {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100%;
      width: 100%;
    }

    & .clearButton {
      display: flex;
      align-items: center;
      justify-content: flex-end;
      height: 100%;
      width: 100%;
      & p {
        margin-right: 6px;
      }
      & .clickable {
        cursor: pointer;
        text-decoration: underline;
        color: red;
      }
    }

    & .stack {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100%;
      width: 100%;
    }
    
    & .dottedBottom {
      border-bottom: 2px dashed black;
      margin-bottom: 3px;
      cursor: default;
    }
    `
  )}
  `

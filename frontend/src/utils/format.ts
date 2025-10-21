export const formatTimestamp = (timestamp: number): string => {
  return new Date(timestamp * 1000).toLocaleString();
};

export const formatDuration = (seconds: number): string => {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  
  if (hours > 0) {
    return `${hours}h ${minutes}m ${secs}s`;
  } else if (minutes > 0) {
    return `${minutes}m ${secs}s`;
  } else {
    return `${secs}s`;
  }
};

export const formatNumber = (num: number, decimals = 2): string => {
  return num.toFixed(decimals);
};

export const formatPressure = (pressure: number): string => {
  return `${pressure.toFixed(2)} bar`;
};

export const formatConcentration = (concentration: number): string => {
  return `${concentration.toFixed(2)} ppm`;
};

export const cn = (...classes: (string | undefined | null | false)[]): string => {
  return classes.filter(Boolean).join(' ');
};

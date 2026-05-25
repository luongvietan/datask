import { HugeiconsIcon, type HugeiconsIconProps } from "@hugeicons/react";

export type IconProp = HugeiconsIconProps["icon"];

interface IconProps extends Omit<HugeiconsIconProps, "icon"> {
  icon: IconProp;
}

export function Icon({ icon, size = 16, strokeWidth = 1.5, className, ...props }: IconProps) {
  return (
    <HugeiconsIcon
      icon={icon}
      size={size}
      strokeWidth={strokeWidth}
      className={className}
      {...props}
    />
  );
}

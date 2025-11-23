interface ButtonWithIconProps {
  text: string;
  iconClassName?: string;
  onClick?: () => void;
  className?: string;
  disabled?: boolean;
}

const ButtonWithIcon: React.FC<ButtonWithIconProps> = ({
  text,
  iconClassName,
  onClick,
  className = '',
  disabled = false,
}) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`
        cursor-pointer px-4 sm:px-6 py-2 border border-white text-white rounded-md hover:bg-(--primary) hover:text-white transition-all duration-300 whitespace-nowrap text-sm sm:text-base inline-block text-center
        ${className}
      `}
    >
      <span className='mr-2'>{text}</span>
      {iconClassName && <i className={iconClassName} />}
    </button>
  );
};

export default ButtonWithIcon;

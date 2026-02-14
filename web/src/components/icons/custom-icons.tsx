import React from 'react';

type IconProps = React.SVGProps<SVGSVGElement>;

export const RavenIcon = ({ className, ...props }: IconProps) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
    {...props}
  >
    {/* Stylized Raven Head/Wing */}
    <path d="M12 2C8 2 4 5 4 10c0 4 3 8 8 10 3-3 6-5 6-9 0-4-3-8-6-9z" />
    <path d="M12 14c-1 0-2-1-2-3s1-3 2-3 2 1 2 3-1 3-2 3z" />
    <path d="M16 8l3-3" />
  </svg>
);

export const ProfessorIcon = ({ className, ...props }: IconProps) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
    {...props}
  >
    {/* Glasses and Bow Tie */}
    <circle cx="6" cy="10" r="3" />
    <circle cx="18" cy="10" r="3" />
    <path d="M9 10h6" />
    <path d="M12 16l-2 2-2-2 2-2 2 2zm0 0l2 2 2-2-2-2-2 2z" />
  </svg>
);

export const ShadowIcon = ({ className, ...props }: IconProps) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
    {...props}
  >
    {/* Spy Hat and Coat Collar */}
    <path d="M4 10h16" />
    <path d="M6 10V6a6 6 0 0 1 12 0v4" />
    <path d="M12 14a4 4 0 0 0-4 4v2h8v-2a4 4 0 0 0-4-4z" />
    <path d="M12 14v-2" />
  </svg>
);

'use client';

import { FC, useState } from 'react';

interface SafetyEmergencyProps {
  emergencyContacts?: {
    Police?: string;
    Ambulance?: string;
    Fire?: string;
    'Tourist Helpline'?: string;
    'State Tourism'?: string;
  };
  safetyInformation?: string[];
}

interface EmergencyContactItem {
  key: string;
  label: string;
  icon: string;
  color: string;
  gradient: string;
  bgColor: string;
}

const SafetyEmergency: FC<SafetyEmergencyProps> = ({
  emergencyContacts,
  safetyInformation,
}) => {
  const [copiedNumber, setCopiedNumber] = useState<string | null>(null);
  const [expandedSafetyTips, setExpandedSafetyTips] = useState<number[]>([]);

  // Emergency contact configurations
  const contactConfigs: EmergencyContactItem[] = [
    {
      key: 'Police',
      label: 'Police',
      icon: 'fa-solid fa-user-shield',
      color: 'text-blue-700',
      gradient: 'from-blue-500 to-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      key: 'Ambulance',
      label: 'Ambulance',
      icon: 'fa-solid fa-truck-medical',
      color: 'text-red-700',
      gradient: 'from-red-500 to-red-600',
      bgColor: 'bg-red-50',
    },
    {
      key: 'Fire',
      label: 'Fire Department',
      icon: 'fa-solid fa-fire-extinguisher',
      color: 'text-orange-700',
      gradient: 'from-orange-500 to-orange-600',
      bgColor: 'bg-orange-50',
    },
    {
      key: 'Tourist Helpline',
      label: 'Tourist Helpline',
      icon: 'fa-solid fa-circle-info',
      color: 'text-purple-700',
      gradient: 'from-purple-500 to-purple-600',
      bgColor: 'bg-purple-50',
    },
    {
      key: 'State Tourism',
      label: 'State Tourism',
      icon: 'fa-solid fa-map-location-dot',
      color: 'text-green-700',
      gradient: 'from-green-500 to-green-600',
      bgColor: 'bg-green-50',
    },
  ];

  const copyToClipboard = async (number: string, label: string) => {
    try {
      await navigator.clipboard.writeText(number);
      setCopiedNumber(label);
      setTimeout(() => setCopiedNumber(null), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const toggleSafetyTip = (index: number) => {
    setExpandedSafetyTips(prev =>
      prev.includes(index) ? prev.filter(i => i !== index) : [...prev, index],
    );
  };

  // Filter out contacts that don't have values
  const availableContacts = contactConfigs.filter(
    config => emergencyContacts?.[config.key as keyof typeof emergencyContacts],
  );

  if (
    (!emergencyContacts || availableContacts.length === 0) &&
    (!safetyInformation || safetyInformation.length === 0)
  ) {
    return null;
  }

  return (
    <div className='w-full py-12 sm:py-16 px-4 bg-gradient-to-br from-slate-50 via-white to-blue-50'>
      {/* Header Section */}
      <div className='text-center mb-8 sm:mb-12'>
        <h2 className='text-3xl sm:text-4xl md:text-5xl font-bold text-gray-800 mb-3 sm:mb-4 font-playfair'>
          Safety & Emergency
        </h2>
        <p className='text-base sm:text-lg text-gray-600 max-w-2xl mx-auto mb-6 sm:mb-8 px-4'>
          Important contacts and safety guidelines for your peace of mind
        </p>
      </div>
      <div className='max-w-7xl mx-auto flex flex-col gap-12 sm:gap-16'>
        {/* Safety Information Section */}
        {safetyInformation && safetyInformation.length > 0 && (
          <div>
            <div className='text-center mb-6 sm:mb-8'>
              <h3 className='text-2xl sm:text-3xl font-bold text-gray-800 mb-2 flex items-center justify-center gap-2 sm:gap-3 px-4'>
                <i className='fa-solid fa-user-shield text-blue-500 text-xl sm:text-2xl' />
                <span>Safety Guidelines</span>
              </h3>
              <p className='text-sm sm:text-base text-gray-600 px-4'>
                Important safety tips to ensure a secure and enjoyable visit
              </p>
            </div>

            {/* Safety Tips Grid */}
            <div className='columns-1 md:columns-2 gap-6 space-y-6'>
              {safetyInformation.map((tip, index) => {
                const isExpanded = expandedSafetyTips.includes(index);
                const shortTip = tip.length > 120 ? tip.substring(0, 120) : tip;
                const needsExpansion = tip.length > 120;

                return (
                  <div
                    key={index}
                    className={`
                      break-inside-avoid mb-6
                      group relative bg-white rounded-2xl shadow-md hover:shadow-2xl
                      transition-all duration-500 transform hover:-translate-y-2 overflow-hidden
                    `}
                    style={{ pageBreakInside: 'avoid' }}
                  >
                    {/* Background Effect */}
                    <div className='absolute inset-0 bg-gradient-to-br from-blue-500 to-cyan-500 opacity-0 group-hover:opacity-5 transition-opacity duration-500' />

                    {/* Content */}
                    <div className='relative p-6'>
                      <div className='flex items-start gap-4'>
                        <div className='flex-1'>
                          {/* Tip Text */}
                          <p className='text-gray-700 leading-relaxed text-base'>
                            {isExpanded || !needsExpansion
                              ? tip
                              : `${shortTip}...`}
                          </p>

                          {/* Expand/Collapse Button */}
                          {needsExpansion && (
                            <button
                              onClick={() => toggleSafetyTip(index)}
                              className='mt-3 text-sm font-medium text-blue-600 cursor-pointer flex items-center gap-2 transition-all duration-300'
                            >
                              {isExpanded ? (
                                <>
                                  <span>Show Less</span>
                                  <i className='fa-solid fa-chevron-up text-xs' />
                                </>
                              ) : (
                                <>
                                  <span>Read More</span>
                                  <i className='fa-solid fa-chevron-down text-xs' />
                                </>
                              )}
                            </button>
                          )}
                        </div>
                      </div>

                      {/* Decorative Corner */}
                      <div className='absolute top-0 right-0 w-20 h-20 opacity-10'>
                        <div className='w-full h-full rounded-bl-full bg-gradient-to-br from-blue-500 to-cyan-500' />
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Emergency Contacts Section */}
        {emergencyContacts && availableContacts.length > 0 && (
          <div>
            <div className='text-center mb-8'>
              <h3 className='text-3xl font-bold text-gray-800 mb-2 flex items-center justify-center gap-3'>
                <i className='fa-solid fa-phone-volume text-red-500' />
                Emergency Contacts
              </h3>
              <p className='text-gray-600'>
                Save these numbers for quick access during emergencies
              </p>
            </div>

            <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'>
              {availableContacts.map(config => {
                const number =
                  emergencyContacts[
                    config.key as keyof typeof emergencyContacts
                  ];
                if (!number) return null;

                return (
                  <div
                    key={config.key}
                    className={`
                      group relative ${config.bgColor} rounded-2xl p-6
                      border-2 border-transparent hover:border-${config.color.split('-')[1]}-300
                      shadow-lg hover:shadow-2xl transition-all duration-300
                      transform hover:-translate-y-2 overflow-hidden
                    `}
                  >
                    {/* Background Pattern */}
                    <div className='absolute top-0 right-0 w-32 h-32 opacity-10'>
                      <div
                        className={`w-full h-full rounded-bl-full bg-gradient-to-br ${config.gradient}`}
                      />
                    </div>

                    {/* Content */}
                    <div className='relative'>
                      {/* Icon */}
                      <div
                        className={`
                          w-16 h-16 rounded-xl bg-gradient-to-br ${config.gradient}
                          flex items-center justify-center mb-4
                          shadow-md group-hover:scale-110 transition-transform duration-300
                        `}
                      >
                        <i className={`${config.icon} text-white text-2xl`} />
                      </div>

                      {/* Label */}
                      <h4
                        className={`text-xl font-bold ${config.color} mb-3 flex items-center gap-2`}
                      >
                        {config.label}
                      </h4>

                      {/* Phone Number */}
                      <div className='flex items-center justify-between gap-3'>
                        <a
                          href={`tel:${number}`}
                          className={`
                            text-2xl font-bold text-gray-800
                            hover:${config.color} transition-colors duration-200
                            flex items-center gap-2
                          `}
                        >
                          <i className='fa-solid fa-phone text-lg' />
                          {number}
                        </a>

                        {/* Copy Button */}
                        <button
                          onClick={() => copyToClipboard(number, config.key)}
                          className={`
                            p-2 rounded-lg ${config.bgColor} ${config.color}
                            hover:bg-gradient-to-br hover:${config.gradient} hover:text-white
                            transition-all duration-300 flex items-center justify-center
                            border border-${config.color.split('-')[1]}-200
                          `}
                          title='Copy number'
                        >
                          {copiedNumber === config.key ? (
                            <i className='fa-solid fa-check text-sm' />
                          ) : (
                            <i className='fa-solid fa-copy text-sm' />
                          )}
                        </button>
                      </div>

                      {/* Copied Notification */}
                      {copiedNumber === config.key && (
                        <div className='mt-2 text-sm text-green-600 font-medium animate-pulse'>
                          <i className='fa-solid fa-check-circle mr-1' />
                          Copied to clipboard!
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Quick Dial Info */}
        <div className='p-6 bg-yellow-50 border-1 border-yellow-500 rounded-lg'>
          <div className='flex items-start gap-4'>
            <div>
              <p className='text-yellow-800 leading-relaxed'>
                In case of an emergency, dial the appropriate number above.
                Always provide your exact location and clearly describe the
                situation. Keep these numbers saved in your phone for quick
                access.
              </p>
            </div>
          </div>
        </div>

        {/* General Safety Banner */}
        <div className='relative overflow-hidden rounded-3xl bg-gradient-to-r from-blue-600 via-blue-500 to-cyan-500 p-8 md:p-12 shadow-2xl'>
          {/* Background Pattern */}
          <div className='absolute inset-0 opacity-10'>
            <div className='absolute top-0 left-0 w-64 h-64 bg-white rounded-full -translate-x-32 -translate-y-32' />
            <div className='absolute bottom-0 right-0 w-96 h-96 bg-white rounded-full translate-x-48 translate-y-48' />
          </div>

          {/* Content */}
          <div className='relative text-center text-white'>
            <h3 className='text-3xl md:text-4xl font-bold mb-4'>
              Your Safety is Our Priority
            </h3>
            <p className='text-lg md:text-xl text-white/95 max-w-3xl mx-auto leading-relaxed'>
              Always stay aware of your surroundings, keep emergency contacts
              handy, and follow local guidelines. If you feel unsafe, don&apos;t
              hesitate to contact the authorities or reach out to your
              accommodation for assistance.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SafetyEmergency;

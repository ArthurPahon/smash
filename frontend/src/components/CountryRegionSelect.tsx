import React from 'react';

interface CountryRegionSelectProps {
  onCountryChange: (country: string) => void;
  onRegionChange: (region: string) => void;
  selectedCountry?: string;
  selectedRegion?: string;
}

const CountryRegionSelect: React.FC<CountryRegionSelectProps> = ({
  onCountryChange,
  onRegionChange,
  selectedCountry,
  selectedRegion,
}) => {
  return (
    <div className="space-y-4">
      <div>
        <label htmlFor="country" className="block text-sm font-medium text-gray-700">
          Pays
        </label>
        <div className="mt-1">
          <input
            type="text"
            id="country"
            value={selectedCountry || ''}
            onChange={e => onCountryChange(e.target.value)}
            className="block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 placeholder-gray-400 shadow-sm focus:border-smash-red focus:outline-none focus:ring-smash-red"
            placeholder="Entrez votre pays"
          />
        </div>
      </div>

      <div>
        <label htmlFor="region" className="block text-sm font-medium text-gray-700">
          Région
        </label>
        <div className="mt-1">
          <input
            type="text"
            id="region"
            value={selectedRegion || ''}
            onChange={e => onRegionChange(e.target.value)}
            className="block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 placeholder-gray-400 shadow-sm focus:border-smash-red focus:outline-none focus:ring-smash-red"
            placeholder="Entrez votre région"
          />
        </div>
      </div>
    </div>
  );
};

export default CountryRegionSelect;

import { Experience } from '@/types/location';

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, '') ||
  'http://localhost:8000';

export interface ApiState {
  _id?: string;
  id: string;
  name: string;
  tagLine?: string;
  labels?: Array<{ id: string; name: string }>;
  images?: {
    banner?: string;
    card?: string;
    others?: string[];
  };
  location?: Array<{
    country: { id: string; name?: string };
    region?: { id: string; name?: string };
    state?: { id: string; name?: string };
  }>;
  description?: {
    title?: string;
    short?: string;
    long?: string;
    overview?: string;
    history?: string;
  };
  greetingText?: string;
  experiences?: {
    Food?: unknown[];
    Activities?: unknown[];
    LocalMarkets?: unknown[];
    Spiritual?: unknown[];
    Historical?: unknown[];
    Nature?: unknown[];
    Cultural?: unknown[];
    Adventure?: unknown[];
    Others?: unknown[];
  };
  travelTips?: string[];
  safetyInformation?: string[];
  emergencyContacts?: {
    Police?: string;
    Ambulance?: string;
    Fire?: string;
    'Tourist Helpline'?: string;
    'State Tourism'?: string;
  };
  [key: string]: unknown;
}

export interface StatesQueryResponse {
  states: ApiState[];
  total: number;
  page: number;
  size: number;
  has_next: boolean;
  has_prev: boolean;
}

/**
 * Fetch states from the API using the query endpoint
 */
export async function fetchStates(
  options: {
    view?: 'minimal' | 'full';
    ids?: string[];
    offset?: number;
    size?: number;
    fetch_all?: boolean;
  } = {}
): Promise<StatesQueryResponse> {
  const {
    view = 'minimal',
    ids = ['t_all'],
    offset = 0,
    size = 100,
    fetch_all = false,
  } = options;

  const response = await fetch(`${API_BASE_URL}/api/v1/states/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      filter: {
        view,
        id: ids,
      },
      offset,
      size,
      fetch_all,
    }),
    cache: 'no-store',
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch states: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch a single state by ID
 */
export async function fetchStateById(stateId: string): Promise<ApiState> {
  // Validate ObjectId format before making the request
  if (!isValidObjectId(stateId)) {
    throw new Error('Invalid state ID format');
  }

  const response = await fetch(`${API_BASE_URL}/api/v1/states/${stateId}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
    cache: 'no-store',
  });

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('State not found');
    }
    if (response.status === 400) {
      // Try to get more details from the response
      try {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Invalid state ID format');
      } catch {
        throw new Error('Invalid state ID format');
      }
    }
    throw new Error(`Failed to fetch state: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Transform API state to frontend State type
 */
/**
 * Transform API state to frontend State type
 */
export function transformApiStateToState(apiState: ApiState) {
  return {
    id: apiState._id || apiState.id || '',
    name: apiState.name,
    tagline: apiState.tagLine,
    labels: apiState.labels?.map((label) => label.name || label.id) || [],
    images: {
      banner: apiState.images?.banner ?? '/images/default.jpg',
      ...(apiState.images?.card && { card: apiState.images.card }),
      ...(apiState.images?.others && { others: apiState.images.others }),
    },
    locations: apiState.location
      ? apiState.location.map((loc) => ({
          country: {
            id: loc.country.id,
            name: loc.country.name || '',
          },
          region: loc.region
            ? {
                id: loc.region.id,
                name: loc.region.name || '',
              }
            : undefined,
          state: loc.state
            ? {
                id: loc.state.id,
                name: loc.state.name || '',
              }
            : undefined,
        }))
      : [],
    description: apiState.description,
    greetingText: apiState.greetingText,
    experiences: apiState.experiences ? (() => {
      // Transform experiences to ensure they're properly formatted
      const transformed: {
        Food?: Experience[];
        Activities?: Experience[];
        LocalMarkets?: Experience[];
        Spiritual?: Experience[];
        Historical?: Experience[];
        Nature?: Experience[];
        Cultural?: Experience[];
        Adventure?: Experience[];
        Others?: Experience[];
      } = {};
      
      // Process each category
      Object.keys(apiState.experiences).forEach(category => {
        const categoryExperiences = apiState.experiences[category as keyof typeof apiState.experiences];
        if (Array.isArray(categoryExperiences)) {
          // Filter out ObjectIds (strings that look like ObjectIds) and keep only objects with name
          const validExperiences = categoryExperiences.filter((exp): exp is Experience => 
            typeof exp === 'object' && 
            exp !== null && 
            'name' in exp &&
            typeof (exp as { name?: unknown }).name === 'string'
          );
          if (validExperiences.length > 0) {
            transformed[category as keyof typeof transformed] = validExperiences;
          }
        }
      });
      
      return Object.keys(transformed).length > 0 ? transformed : undefined;
    })() : undefined,
    travelTips: apiState.travelTips,
    safetyInformation: apiState.safetyInformation,
    emergencyContacts: apiState.emergencyContacts,
  };
}

export interface ApiCity {
  _id: string;
  id?: string;
  name: string;
  state_id: string;
  is_active: boolean;
  tagLine?: string;
  location?: Array<{
    country: { id: string; name?: string };
    region?: { id: string; name?: string };
    state?: { id: string; name?: string };
  }>;
  description?: {
    title?: string;
    short?: string;
    long?: string;
    overview?: string;
    history?: string;
  };
  greetingText?: string;
  images?: {
    banner?: string;
    card?: string;
    others?: string[];
  };
  experiences?: {
    Food?: unknown[];
    Activities?: unknown[];
    LocalMarkets?: unknown[];
    Spiritual?: unknown[];
    Historical?: unknown[];
    Nature?: unknown[];
    Cultural?: unknown[];
    Adventure?: unknown[];
    Others?: unknown[];
  };
  travelTips?: string[];
  safetyInformation?: string[];
  emergencyContacts?: {
    Police?: string;
    Ambulance?: string;
    Fire?: string;
    'Tourist Helpline'?: string;
    'State Tourism'?: string;
  };
  [key: string]: unknown;
}

export interface CitiesListResponse {
  cities: ApiCity[];
  total: number;
  page: number;
  size: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface Label {
  id: string;
  name: string;
}

export interface LabelsResponse {
  labels: Label[];
}

/**
 * Fetch all labels from the API
 */
export async function fetchLabels(): Promise<LabelsResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/labels/`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
    cache: 'no-store',
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch labels: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Query cities using the flexible query endpoint
 */
export async function queryCities(options: {
  offset?: number;
  size?: number;
  search?: string;
  state_id?: string | string[];
  labels?: string[];
  label_filter_type?: 'any' | 'all';
  view?: 'minimal' | 'full';
} = {}): Promise<CitiesListResponse> {
  const {
    offset = 0,
    size = 20,
    search,
    state_id,
    labels,
    label_filter_type = 'any',
    view = 'full',
  } = options;

  interface CityQueryFilter {
    view: 'minimal' | 'full';
    id: string[];
    search?: string;
    state_id?: string[];
    labels?: string[];
    label_filter_type?: 'any' | 'all';
  }

  const filter: CityQueryFilter = {
    view,
    id: ['t_all'],
  };

  if (search) {
    filter.search = search;
  }

  if (state_id) {
    filter.state_id = Array.isArray(state_id) ? state_id : [state_id];
  }

  if (labels && labels.length > 0) {
    filter.labels = labels;
    filter.label_filter_type = label_filter_type;
  }

  const response = await fetch(`${API_BASE_URL}/api/v1/cities/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      filter,
      offset,
      size,
      fetch_all: false,
    }),
    cache: 'no-store',
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch cities: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch cities from the API (legacy endpoint - kept for backward compatibility)
 */
export async function fetchCities(options: {
  skip?: number;
  limit?: number;
  search?: string;
  state_id?: string;
  is_active?: boolean;
} = {}): Promise<CitiesListResponse> {
  const {
    skip = 0,
    limit = 20,
    search,
    state_id,
    is_active,
  } = options;

  const params = new URLSearchParams({
    skip: skip.toString(),
    limit: limit.toString(),
  });

  if (search) {
    params.append('search', search);
  }
  if (state_id) {
    params.append('state_id', state_id);
  }
  if (is_active !== undefined) {
    params.append('is_active', is_active.toString());
  }

  const response = await fetch(
    `${API_BASE_URL}/api/v1/cities/?${params.toString()}`,
    {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      cache: 'no-store',
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch cities: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Validate MongoDB ObjectId format (24 hex characters)
 */
function isValidObjectId(id: string): boolean {
  return /^[0-9a-fA-F]{24}$/.test(id);
}

/**
 * Fetch a single city by ID
 */
export async function fetchCityById(cityId: string): Promise<ApiCity> {
  // Validate ObjectId format before making the request
  if (!isValidObjectId(cityId)) {
    throw new Error('Invalid city ID format');
  }

  const response = await fetch(`${API_BASE_URL}/api/v1/cities/${cityId}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
    cache: 'no-store',
  });

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('City not found');
    }
    if (response.status === 400) {
      // Try to get more details from the response
      try {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Invalid city ID format');
      } catch {
        throw new Error('Invalid city ID format');
      }
    }
    throw new Error(`Failed to fetch city: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Transform API city to frontend City type
 */
export function transformApiCityToCity(apiCity: ApiCity) {
  return {
    id: apiCity._id || apiCity.id || '',
    name: apiCity.name,
    tagline: apiCity.tagLine,
    images: {
      banner: apiCity.images?.banner ?? '/images/default.jpg',
      ...(apiCity.images?.card && { card: apiCity.images.card }),
      ...(apiCity.images?.others && { others: apiCity.images.others }),
    },
    locations: apiCity.location
      ? apiCity.location.map((loc) => ({
          country: {
            id: loc.country.id,
            name: loc.country.name || '',
          },
          region: loc.region
            ? {
                id: loc.region.id,
                name: loc.region.name || '',
              }
            : undefined,
          state: loc.state
            ? {
                id: loc.state.id,
                name: loc.state.name || '',
              }
            : undefined,
        }))
      : [],
    description: apiCity.description,
    greetingText: apiCity.greetingText,
    labels: [], // Cities might not have labels in the API
    experiences: apiCity.experiences,
    travelTips: apiCity.travelTips,
    safetyInformation: apiCity.safetyInformation,
    emergencyContacts: apiCity.emergencyContacts,
  };
}


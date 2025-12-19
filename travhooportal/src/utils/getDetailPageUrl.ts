import { TYPE_TO_PAGE_MAP } from '../constants';

const getDetailPageUrl = (id: string, type: string) => {
  // Handle empty or invalid IDs
  if (!id || id.trim() === '') {
    console.warn(`getDetailPageUrl: Empty ID provided for type "${type}"`);
    // Return a fallback URL that will show an error page
    return `/detail/${TYPE_TO_PAGE_MAP.detail[type as keyof typeof TYPE_TO_PAGE_MAP.detail]}/invalid`;
  }
  return `/detail/${TYPE_TO_PAGE_MAP.detail[type as keyof typeof TYPE_TO_PAGE_MAP.detail]}/${id}`;
};

export default getDetailPageUrl;

import axios from 'axios';
import { A2AMessage, BaseAgent, Tool } from '../base/Agent';

interface FlightSearchParams {
    origin: string;
    destination: string;
    departureDate: string;
    returnDate?: string;
    passengers?: number;
    cabinClass?: string;
}

class FlightSearchTool implements Tool {
    name = 'flight_search';
    description = 'Search for flights using AWS Lambda backend';

    constructor(private awsApiUrl: string, private apiKey: string) {}

    async execute(params: FlightSearchParams): Promise<Record<string, any>> {
        try {
            const response = await axios.post(`${this.awsApiUrl}/flight-search`,
            params,
                {
                    headers: {
                    'x-api-key': this.apiKey,
                    'Content-Type': 'application/json'
                    },
                    timeout: 25000
                }
            );
            return {
                status: 'success',
                flights: response.data.flights || [],
                searchCriteria: params
            };
        } catch (error) {
            return {
                status: 'error',
                message: axios.isAxiosError(error) ? error.message : 'Flight search failed',
                searchCriteria: params
            };
        }
    }
}


class PriceAnalysisTool implements Tool {
    name = 'price_analysis';
    description = 'Analyze flight prices and provide recommendations';

    async execute(params: { flights: any[], criteria: Record<string, any> }) {
        const { flights } = params;

        if (!flights || flights.length === 0) {
            return { status: 'no_data', message: 'No flights to analyze' };
        }
        
        const prices = flights
        .map(flight => parseFloat(flight.price || '0'))
        .filter(price => price > 0);

        if (prices.length === 0) {
            return { status: 'no_prices', message: 'No valid price data' };
        }
        const minPrice = Math.min(...prices);
        const maxPrice = Math.max(...prices);
        const avgPrice = prices.reduce((sum, price) => sum + price, 0) / prices.length;
        return {
            status: 'success',
            priceRange: { min: minPrice, max: maxPrice, average: avgPrice },
            recommendations: [
                {
                type: 'best_value',
                flightIndex: flights.findIndex(f => parseFloat(f.price || '0') === minPrice),
                reason: 'Lowest price option'
                }
            ]
        };
    }
}

export class FlightSpecialist extends BaseAgent {
    constructor(awsApiUrl: string, apiKey: string) {
        const tools = [
            new FlightSearchTool(awsApiUrl, apiKey),
            new PriceAnalysisTool()
        ];
        super(
            'flight-specialist',
            'Expert in flight searches, bookings, and price analysis',
            tools
        );
    }


    async processRequest(request: Record<string, any>): Promise<Record<string,any>> {
        const { action, parameters } = request;
        switch (action) {
            case 'search_flights':
                return await this.searchFlights(parameters);
            case 'analyze_prices':
                return await this.analyzePrices(parameters);
            default:
            return {
                status: 'error',
                message: `Unknown action: ${action}`,
                supportedActions: ['search_flights', 'analyze_prices']
                };
        }
    }

    async processA2ARequest(message: A2AMessage): Promise<Record<string, any>> {
        const { action, parameters } = message.payload;
        this.memory.addMessage('system', `A2A request: ${action} from ${message.fromAgent}`);
        return await this.processRequest({ action, parameters });
    }

    private async searchFlights(params: FlightSearchParams): Promise<Record<string, any>> {
        try {
            this.status = 'processing' as any;
            const result = await this.useTool('flight_search', params);
            if (result.status === 'success' && result.flights.length > 0) {
                const priceAnalysis = await this.useTool('price_analysis', {
                    flights: result.flights,
                    criteria: params
                });
                result.priceAnalysis = priceAnalysis;
                this.memory.addMessage(
                    'system',
                    `Flight search: ${params.origin} to ${params.destination}, found
                    ${result.flights.length} options`
                );
            }
            return result;
        } catch (error) {
            return {
                status: 'error',
                message: `Flight search failed: ${(error as Error).message}`,
                parameters: params
            };
        } finally {
            this.status = 'idle' as any;
        }
    }

    private async analyzePrices(params: Record<string, any>):Promise<Record<string, any>> {
        return await this.useTool('price_analysis', params);
    }
}


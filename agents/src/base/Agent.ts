import { EventEmitter } from 'events';
import { v4 as uuidv4 } from 'uuid';
import { logger } from '../utils/logger';

export enum AgentStatus {
    IDLE = 'idle',
    PROCESSING = 'processing',
    ERROR = 'error',
    OFFLINE = 'offline'
}

export enum MessageType {
    REQUEST = 'request',
    RESPONSE = 'response',
    EVENT = 'event',
    HEARTBEAT = 'heartbeat'
}

export interface A2AMessage {
    id: string;
    fromAgent: string;
    toAgent: string;
    messageType: MessageType;
    payload: Record<string, any>;
    conversationId?: string;
    timestamp: Date;
    correlationId?: string;
}

export interface Tool {
    name: string;
    description: string;
    execute: (params: Record<string, any>) => Promise<Record<string, any>>;
}

export interface Memory {
    conversationHistory: Array<{
        role: string;
        content: string;
        timestamp: Date;
        metadata?: Record<string, any>;
    }>;
    userContext: Record<string, any>;

    addMessage(role: string, content: string, metadata?: Record<string, any>): void;
    getContext(): Array<any>;
    updateUserContext(context: Record<string, any>): void;
}
export class SimpleMemory implements Memory {
    conversationHistory: Array<{
        role: string;
        content: string;
        timestamp: Date;
        metadata?: Record<string, any>;
    }> = [];
    userContext: Record<string, any> = {};
    constructor(private maxMessages: number = 10) {}
    addMessage(role: string, content: string, metadata?: Record<string, any>): void {
        this.conversationHistory.push({
            role,
            content,
            timestamp: new Date(),
            metadata
        });

        if (this.conversationHistory.length > this.maxMessages) {
            this.conversationHistory = this.conversationHistory.slice(this.maxMessages);
        }
    }

    getContext(): Array<any> {
        return this.conversationHistory;
    }

    updateUserContext(context: Record<string, any>): void {
        this.userContext = { ...this.userContext, ...context };
    }
}

export abstract class BaseAgent extends EventEmitter {
    protected status: AgentStatus = AgentStatus.IDLE;
    protected tools: Map<string, Tool> = new Map();
    protected memory: Memory;
    protected pendingRequests: Map<string, Function> = new Map();

    constructor(
        public name: string,
        public description: string,
        tools: Tool[] = [],
        memory?: Memory
    ) {
        super();

        // Initialize tools
        tools.forEach(tool => this.addTool(tool));

        // Initialize memory
        this.memory = memory || new SimpleMemory();
        logger.info(`Initializing agent: ${this.name}`);
    }

    async initialize(): Promise<void> {
        logger.info(`Agent ${this.name} initialized`);
        this.status = AgentStatus.IDLE;
        this.emit('initialized');
    }

    addTool(tool: Tool): void {
        this.tools.set(tool.name, tool);
        logger.info(`Added tool ${tool.name} to agent ${this.name}`);
    }

    async useTool(toolName: string, params: Record<string, any>): Promise<Record<string, any>> {
        const tool = this.tools.get(toolName);
        if (!tool) {
            throw new Error(`Tool ${toolName} not found`);
        }

        logger.info(`Agent ${this.name} using tool: ${toolName}`);
        return await tool.execute(params);
    }

    async sendA2AMessage(
        toAgent: string,
        messageType: MessageType,
        payload: Record<string, any>,
        conversationId?: string
    ): Promise<string> {
        const message: A2AMessage = {
            id: uuidv4(),
            fromAgent: this.name,
            toAgent,
            messageType,
            payload,
            conversationId,
            timestamp: new Date()
        };

        // Emit for message bus to handle
        this.emit('a2a-message', message);
        return message.id;
    }

    async handleA2AMessage(message: A2AMessage): Promise<void> {
        logger.info(`Agent ${this.name} received A2A message fromv${message.fromAgent}`);
        try {
            if (message.messageType === MessageType.REQUEST) {
                const response = await this.processA2ARequest(message);

                if (response) {
                    await this.sendA2AMessage(
                        message.fromAgent,
                        MessageType.RESPONSE,
                        response,
                        message.conversationId
                    );
                }

            } else if (message.messageType === MessageType.RESPONSE) {
                await this.handleA2AResponse(message);
            }
        } catch (error) {
            logger.error(`Error handling A2A message in ${this.name}:`, error);

            // Send error response
            await this.sendA2AMessage(
                message.fromAgent,
                MessageType.RESPONSE,
                { status: 'error', message: (error as Error).message },
                message.conversationId
            );
        }
    }

    abstract processRequest(request: Record<string, any>): Promise<Record<string, any>>;

    abstract processA2ARequest(message: A2AMessage): Promise<Record<string, any>>;

    async handleA2AResponse(message: A2AMessage): Promise<void> {
        const callback = this.pendingRequests.get(message.correlationId || '');
        if (callback) {
            this.pendingRequests.delete(message.correlationId || '');
            callback(message.payload);
        }
    }
        
    getStatus(): AgentStatus {
        return this.status;
    }
    
    getMemory(): Memory {
        return this.memory;
    }
}

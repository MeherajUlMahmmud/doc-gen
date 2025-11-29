import React from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { FileText, CalendarDays } from 'lucide-react';
import type { Template } from '@/types/document';
import { format } from 'date-fns';

interface TemplateCardProps {
    template: Template;
}

export const TemplateCard: React.FC<TemplateCardProps> = ({ template }) => {
    const formattedDate = format(new Date(template.created_at), 'MMM d, yyyy');

    return (
        <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
                <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                        <div className="p-3 bg-primary/10 rounded-lg">
                            <FileText className="h-6 w-6 text-primary" />
                        </div>
                        <div>
                            <CardTitle className="text-lg">{template.title}</CardTitle>
                            <CardDescription className="flex items-center gap-2 mt-1">
                                <CalendarDays className="h-3 w-3" />
                                {formattedDate}
                            </CardDescription>
                        </div>
                    </div>
                    <div className="flex flex-col gap-1 items-end">
                        <Badge variant="outline">v{template.version}</Badge>
                    </div>
                </div>
            </CardHeader>

            {template.description && (
                <CardContent>
                    <p className="text-sm text-muted-foreground line-clamp-2">
                        {template.description}
                    </p>
                </CardContent>
            )}

            <CardFooter className="flex gap-2">
                <Button asChild className="flex-1">
                    <Link to={`/documents/new?template=${template.id}`}>
                        Use Template
                    </Link>
                </Button>
                <Button asChild variant="outline">
                    <Link to={`/templates/${template.id}`}>
                        View Details
                    </Link>
                </Button>
            </CardFooter>
        </Card>
    );
};

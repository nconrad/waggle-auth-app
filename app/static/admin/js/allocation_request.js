/**
 * Allocation Request Admin JavaScript
 *
 * This script manages the dynamic behavior of the AllocationRequest admin form.
 * It controls the visibility of form fields based on the selected project request type:
 * - When "Request new project" is selected, it shows the project details form and hides the existing project dropdown
 * - When "Renew existing project" or "Request add to existing project" is selected, it shows the existing project dropdown
 *
 */

(function($) {
    $(document).ready(function() {
        // Cache DOM elements for better performance
        var existingProjectRow = $('.field-existing_project');
        var projectRequestTypeRadios = $('input[name="project_request_type"]');
        var projectDetailsSection = $('.project-details');
        var accessPermissionsSection = $('.access-permissions');
        var hpcInterestSection = $('.hpc-interest');

        // Debug logging
        console.log('Found existing project row:', existingProjectRow.length > 0);
        console.log('Found project details section:', projectDetailsSection.length > 0);
        console.log('Found access permissions section:', accessPermissionsSection.length > 0);
        console.log('Found HPC interest section:', hpcInterestSection.length > 0);

        /**
         * Updates the visibility of the existing project dropdown field
         *
         * Shows the field when "Renew existing project" or "Request add to existing project" is selected,
         * and hides it when "Request new project" is selected.
         * Also sets the field as required when it's visible.
         */
        function updateExistingProjectVisibility() {
            var selectedValue = $('input[name="project_request_type"]:checked').val();
            var shouldShow = selectedValue === 'renew' || selectedValue === 'add';

            console.log('Selected value:', selectedValue);
            console.log('Should show existing project:', shouldShow);

            if (existingProjectRow.length) {
                existingProjectRow.toggle(shouldShow);
                $('#id_existing_project').prop('required', shouldShow);
            } else {
                console.error('Could not find existing project row');
            }
        }

        /**
         * Updates the visibility of the project details sections
         *
         * Shows the sections when "Request new project" is selected,
         * and hides them for other options.
         * Also sets fields as required when visible.
         */
        function updateProjectDetailsVisibility() {
            var selectedValue = $('input[name="project_request_type"]:checked').val();
            var shouldShow = selectedValue === 'new';

            console.log('Should show project details:', shouldShow);

            // Toggle visibility of all sections
            projectDetailsSection.toggle(shouldShow);
            accessPermissionsSection.toggle(shouldShow);
            hpcInterestSection.toggle(shouldShow);

            // Make fields required when visible
            if (shouldShow) {
                // Required fields for new projects
                var requiredFields = [
                    'pi_name', 'pi_email', 'pi_institution',
                    'project_title', 'project_short_name',
                    'science_fields', 'related_to_proposal',
                    'funding_sources'
                ];

                requiredFields.forEach(function(fieldName) {
                    $('#id_' + fieldName).prop('required', true);
                });
            } else {
                // Remove required attribute from all fields
                projectDetailsSection.find('input, select, textarea').prop('required', false);
                accessPermissionsSection.find('input, select, textarea').prop('required', false);
                hpcInterestSection.find('input, select, textarea').prop('required', false);
            }
        }

        // Debug: Log all radio values and their labels
        projectRequestTypeRadios.each(function() {
            console.log('Radio value:', $(this).val(), 'Label:', $(this).parent().text().trim());
        });

        // Add change event listeners to all radio buttons
        projectRequestTypeRadios.on('change', function() {
            console.log('Radio changed to:', $(this).val());
            updateExistingProjectVisibility();
            updateProjectDetailsVisibility();
        });

        // Set initial visibility state when the page loads
        updateExistingProjectVisibility();
        updateProjectDetailsVisibility();
    });
})(django.jQuery);
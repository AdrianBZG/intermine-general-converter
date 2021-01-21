package org.intermine.bio.dataconversion;

/*
 * Copyright (C) 2002-2018 FlyMine
 *
 * This code may be freely distributed and modified under the
 * terms of the GNU Lesser General Public Licence.  This should
 * be distributed with the code.  See the LICENSE file for more
 * information or http://www.gnu.org/copyleft/lesser.html.
 *
 */

import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.io.Reader;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;

import org.apache.commons.lang.StringUtils;
import org.apache.log4j.Logger;
import org.intermine.dataconversion.ItemWriter;
import org.intermine.metadata.Model;
import org.intermine.objectstore.ObjectStoreException;
import org.intermine.util.FormattedTextParser;
import org.intermine.xml.full.Item;

public class SkeletonConverter extends BioDirectoryConverter
{
    private static final String DATASET_TITLE = "Skeleton Converter Dataset Title";
    private static final String DATA_SOURCE_NAME = "Skeleton Converter Source Name";
    private static final String TAXON_ID = "9606";
    private static final String INPUT_FILE = "input_file.format";

    protected IdResolver rslv;
    private String organismIdentifier;
    private static final Logger LOG = Logger.getLogger(SkeletonConverter.class);

    public SkeletonConverter(ItemWriter writer, Model model) {
        super(writer, model, DATA_SOURCE_NAME, DATASET_TITLE);
        if (rslv == null) {
            rslv = IdResolverService.getIdResolverByOrganism(TAXON_ID);
        }
    }

    public void process(File dataDir) throws Exception {
        Map<String, File> files = readFilesInDir(dataDir);
        organismIdentifier = getOrganism(TAXON_ID);
        processData(new FileReader(files.get(INPUT_FILE)));
    }

    private Map<String, File> readFilesInDir(File dir) {
        Map<String, File> files = new HashMap<String, File>();
        for (File file : dir.listFiles()) {
            files.put(file.getName(), file);
        }
        return files;
    }

    private void processData(Reader reader) throws ObjectStoreException, IOException {
        // Process code
    }

    private String resolveGene(String identifier) {
        String id = identifier;
        if (rslv != null && rslv.hasTaxon(TAXON_ID)) {
            int resCount = rslv.countResolutions(TAXON_ID, identifier);
            if (resCount != 1) {
                return null;
            }
            id = rslv.resolveId(TAXON_ID, identifier).iterator().next();
        }
        return id;
    }
}
